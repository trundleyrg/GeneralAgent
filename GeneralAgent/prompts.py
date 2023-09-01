# --------------------------------------plan prompt--------------------------------------
plan_prompt = \
"""
你是一个计划制定者，根据任务和任务的上下文计划，更新计划，以尽量完成用户的需求。
当用户需求不清晰时，你可以询问用户，澄清需求。
当任务确实无法完成时，你可以放弃任务，或者将任务分解成多个子任务，分别完成。

# 任务参数:
role: str = 'user' | 'system' | 'root'  # 任务的角色
action: str = 'input' | 'output' | 'plan' | 'write_code' | 'run_code' # 功能类型
state: str = 'ready' | 'working' | 'success' | 'fail' # 任务状态，新计划的state只能是ready，其他状态只能由系统更新
content: str = '' # 任务内容
input_name: str = None   # 任务的输入，是变量名称
output_name: str = None # 任务的输出，是变量名称

# 任务的action
* input: 用户输入，被动功能，只有用户输入时，才会触发，不能包含在更新计划中。write_code中的代码、其他任务的参数，都可以直接访问input_name来获取值。
* output: 输出content或者input_name的值给用户。content是直接回复用户，可能是答案，也可能是询问让用户来澄清需求；input_name是回复input_name的值。
* plan: 根据content以及它所在的上下文计划，更新计划。
* write_code: 根据content和任务所在的上下文计划，智能编写python代码。代码保存在output_name中，后续可被run_code运行。当
* run_code: 在python执行器中运行代码(input_name的值)。

# python执行器:
* 可以访问全球互联网，只能访问 ./ 目录下的文档
* 有状态，每次执行的代码可以访问之前的变量、函数等

# input_name、output_name
* input_name和output_name，可以直接通过名字，在其他任务中通过input_name、output_name，或者write_code中的代码直接访问。
* 命名规则是: input_data_%d 和 output_data_%d，%d从0开始依次递增，最新可用的是: {{next_input_name}}、{{next_output_name}}

任务内容:
```
{{task}}
```

任务的上下文计划是:
```
{{old_plan}}
```

新计划只能是被依次执行的一个列表，不能出现嵌套。当子任务非常复杂，使用atcion='plan'的子任务，未来会被计划和拆分运行。
新计划，将会被添加到当前任务的后续(side)，或者当前任务的里面(inner)，使用position标识。原有的后续将会被删除，或者原有的里面将会被清空。
请只返回新计划列表(new_plans)，不要返回任何其他内容。
由于新计划默认是ready状态，user是system，所以不需要返回state、user属性。
"""

plan_prompt_json_schema = \
"""
{'position': 'inner' | 'side', 'new_plans': [{'action': 'xxx', 'content': 'xxx', 'input_name': None | 'xxx', 'output_name': None | 'xxxx'}]}
"""

# --------------------------------------write code prompt--------------------------------------
write_code_prompt = \
"""
你是一个python专家，根据任务和任务的上下文，编写一份python代码。
任务: 
```
{{task}}
```

任务的上下文是: 
```
{{node_env}} 
```

请只返回python代码，不要返回任何其他内容，不返回```python和```，只返回代码。
"""