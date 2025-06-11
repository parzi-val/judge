import logging
import asyncio
import re
from typing import Optional, Union
from core.slm_wrapper import SLMWrapper
from core.policy import Policy

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class EvaluationNode:
    def __init__(self, value: Union[str, SLMWrapper], policy: Optional[Policy] = None):
        self.value = value
        self.policy = policy
        self.left: Optional["EvaluationNode"] = None
        self.right: Optional["EvaluationNode"] = None
        self.result: Optional[str] = None

    def is_leaf(self) -> bool:
        return isinstance(self.value, SLMWrapper)


class EvaluationEngine:
    def __init__(self):
        self.root: Optional[EvaluationNode] = None
        self.result_map: dict[str, str] = {}

    def construct_tree_from_statement(self, statement: str, policy_map: dict[str, Policy], slm_map: dict[str, SLMWrapper]):
        """
        Parses a logical statement and constructs the evaluation tree.
        """
        def tokenize(expr: str):
            return re.findall(r'\(|\)|AND|OR|NOT|[a-zA-Z_]+', expr)

        def precedence(op: str) -> int:
            return {"OR": 1, "AND": 2, "NOT": 3}.get(op, 0)

        def build_expression_tree(tokens):
            values = []
            ops = []

            def apply_op():
                op = ops.pop()
                if op == "NOT":
                    right = values.pop()
                    node = EvaluationNode("NOT")
                    node.left = right
                    values.append(node)
                else:
                    right = values.pop()
                    left = values.pop()
                    node = EvaluationNode(op)
                    node.left = left
                    node.right = right
                    values.append(node)

            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token == '(':
                    ops.append(token)
                elif token == ')':
                    while ops and ops[-1] != '(':
                        apply_op()
                    ops.pop()  # remove '('
                elif token.upper() in ("AND", "OR", "NOT"):
                    while (ops and precedence(ops[-1]) >= precedence(token.upper())):
                        apply_op()
                    ops.append(token.upper())
                else:
                    alias = token
                    policy = policy_map[alias]
                    slm = slm_map[alias]
                    values.append(EvaluationNode(slm, policy))
                i += 1

            while ops:
                apply_op()

            return values[-1] if values else None

        tokens = tokenize(statement)
        self.root = build_expression_tree(tokens)
        logging.info("Evaluation tree constructed from logical statement.")

    async def _evaluate_node(self, node: EvaluationNode, user_input) -> str:
        if node is None:
            return "unknown"

        if node.is_leaf():
            logging.info(f"Evaluating SLM node: {node.value.name} for policy '{node.policy.name}'")
            policy_name, result = await node.value(node.policy, user_input)
            node.result = result
            self.result_map[node.value.name] = result

            logging.info(f"Result from SLM '{node.value.name}': {result}")
            return result

        logging.info(f"Evaluating operator node: '{node.value}'")

        left_task = asyncio.create_task(self._evaluate_node(node.left, user_input)) if node.left else None
        right_task = asyncio.create_task(self._evaluate_node(node.right,user_input)) if node.right else None

        left_result = await left_task if left_task else None
        right_result = await right_task if right_task else None

        logic = node.value.upper()
        logging.info(f"Combining results: {left_result} {logic} {right_result}")

        if logic == "OR":
            node.result = "violation" if left_result == "violation" and right_result == "violation" else "compliant"
        elif logic == "AND":
            node.result = "violation" if left_result == "violation" or right_result == "violation" else "compliant"
        elif logic == "NOT":
            node.result = "compliant" if left_result == "violation" else "violation"
        else:
            node.result = "unknown"

        logging.info(f"Result of node '{logic}': {node.result}")
        return node.result

    async def evaluate(self, user_input) -> str:
        if not self.root:
            raise ValueError("Evaluation tree not initialized.")
        logging.info("Starting evaluation of the tree...")
        result = await self._evaluate_node(self.root, user_input)
        logging.info(f"Final decision: {result.upper()}")
        return result, self.result_map 
