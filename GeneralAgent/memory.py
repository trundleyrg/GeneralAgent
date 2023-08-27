# 记忆
import datetime
# 存储所有记忆，优点是: 实时逐步序列化，即使程序崩溃了也记录了
from tinydb import TinyDB, Query

ConceptNodeTypes = ['input', 'output', 'thought', 'plan', 'action']
ConceptNodeStates = ['ready', 'done', 'cancel', 'fail'] # 状态只能从ready转移到其他三个中去


# 记忆节点
class ConceptNode:
    @classmethod
    def from_dict(cls, dict):
        return cls(dict['type'], dict['concept'], dict['create_at'], dict['concept_embedding'], dict['priority'], dict['create_at'], dict['state'], dict['from_nodes'], dict['to_nodes'])

    def __init__(self, type, index, concept, concept_embedding, priority, create_at=None, state='done', from_nodes=[], to_nodes=[]):
        # 验证
        assert type in ConceptNodeTypes
        assert state in ConceptNodeStates
        if type == 'plan':
            assert concept.startswith('[plan]') or concept.startswith('[action]') or concept.startswith('[response]')
        # 赋值
        self.type = type    # string: input, output, thought, plan, action
        self.index = index  # 索引 int
        self.concept = concept  # 概念 string
        self.concept_embedding = concept_embedding # 概念embedding ([float])
        self.priority = priority    # 重要性 (float: 0~10)
        self.create_at = create_at or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 创建时间, string
        self.state = state  # 状态 string: ready、done、cancel
        self.from_nodes = from_nodes        # 来源 [index]
        self.to_nodes = to_nodes        # 被引用 -> 一般都是计划实行情况 [index]

    def __str__(self) -> str:
        return f'[{self.type}] {self.index} {self.state} {self.create_at} {self.concept}'


# 记忆
class Memory:
    def __init__(self, file_path, embedding_fun=None) -> None:
        # file_path: 存储路径，比如 xxx.json
        # embedding_fun: 用于计算概念的embedding
        self.embedding_fun = embedding_fun
        self.db = TinyDB(file_path)
        self.concept_nodes = [ConceptNode.from_dict(record) for record in self.db.all()]

    def add_concept(self, type, concept, concept_embedding=None):
        if concept_embedding is None:
            concept_embedding = self.embedding_fun(concept)
        
        priority = 1
        # TODO: 计算优先级
        concept_node = ConceptNode(type, len(self.concept_nodes), concept, concept_embedding=concept_embedding, priority=priority)
        self.concept_nodes.append(concept_node)
        
        # 保存
        self.db.insert(concept_node.__dict__)

        # TODO: 触发反思

        return concept_node
    
    # 更新概念节点
    def update_concept(self, concept_node: ConceptNode):
        self.db.update(concept_node.__dict__, Query().index == concept_node.index)

    def get_concept_with_type(self, type):
        # 获取某种类型的概念
        return [concept_node for concept_node in self.concept_nodes if concept_node.type == type]
    
    def get_plan_in_plan(self):
        # 获取计划中的计划
        return [x for x in self.concept_nodes if x.type == 'plan' and x.concept.startswith('[plan]')]
    
    def retrieve(self, focus_points):
        # 检索, focus_points 是关注的点，
        pass