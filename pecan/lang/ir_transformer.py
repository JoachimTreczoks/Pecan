#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ir import *

class IRTransformer:
    def __init__(self):
        self.current_program = None

    def transform[T : IRNode](self, node : T) -> T:
        if node is None:
            return None
        elif isinstance(node, str):
            return self.transform_str(node)
        else:
            return node.transform(self)

    def transform_str(self, node : str) -> str:
        return node

    def transform_decl_type(self, t):
        from pecan.lang.type_inference import RestrictionType
        if isinstance(t, Call):
            return RestrictionType(self.transform(t))
        else:
            return t

    def transform_Conjunction(self, node : Conjunction) -> Conjunction:
        return Conjunction(self.transform(node.a), self.transform(node.b))

    def transform_Disjunction(self, node : Disjunction) -> Disjunction:
        return Disjunction(self.transform(node.a), self.transform(node.b))

    def transform_Complement(self, node : Complement) -> Complement:
        return Complement(self.transform(node.a))

    def transform_BoolConst(self, node : BoolConst) -> BoolConst:
        return BoolConst(node.bool_val)

    def transform_DirectiveSaveAut(self, node : DirectiveSaveAut) -> DirectiveSaveAut:
        return DirectiveSaveAut(self.transform(node.filename), self.transform(node.pred_name))

    def transform_DirectiveSaveAutImage(self, node : DirectiveSaveAutImage) -> DirectiveSaveAutImage:
        return DirectiveSaveAutImage(self.transform(node.filename), self.transform(node.pred_name))

    def transform_DirectiveContext(self, node : DirectiveContext) -> DirectiveContext:
        return DirectiveContext(self.transform(node.context_key), self.transform(node.context_val))

    def transform_DirectiveEndContext(self, node : DirectiveEndContext) -> DirectiveEndContext:
        return DirectiveEndContext(self.transform(node.context_key))

    def transform_DirectiveAssertProp(self, node : DirectiveAssertProp) -> DirectiveAssertProp:
        return DirectiveAssertProp(self.transform(node.truth_val), self.transform(node.pred_name))

    def transform_DirectiveLoadAut(self, node : DirectiveLoadAut) -> DirectiveLoadAut:
        return DirectiveLoadAut(self.transform(node.filename), self.transform(node.aut_format), self.transform(node.pred))

    def transform_DirectiveImport(self, node : DirectiveImport) -> DirectiveImport:
        return DirectiveImport(self.transform(node.filename))

    def transform_DirectiveForget(self, node : DirectiveForget) -> DirectiveForget:
        return DirectiveForget(self.transform(node.var_name))

    def transform_DirectiveStructure(self, node : DirectiveStructure) -> DirectiveStructure:
        return DirectiveStructure(self.transform_decl_type(node.pred_ref),
                {self.transform(k): self.transform(v) for k, v in node.val_dict.items()})

    def transform_DirectiveShuffle(self, node : DirectiveShuffle) -> DirectiveShuffle:
        return DirectiveShuffle(node.disjunction, self.transform(node.pred_a), self.transform(node.pred_b), self.transform(node.output_pred))

    def transform_Add(self, node : Add) -> Add:
        return Add(self.transform(node.a), self.transform(node.b)).with_type(node.get_type())

    def transform_Sub(self, node : Sub) -> Sub:
        return Sub(self.transform(node.a), self.transform(node.b)).with_type(node.get_type())

    def transform_Mul(self, node : Mul) -> Mul:
        return Mul(self.transform(node.a), self.transform(node.b)).with_type(node.get_type())

    def transform_IntConst(self, node : IntConst) -> IntConst:
        return node

    def transform_Equals(self, node : Equals) -> Equals:
        return Equals(self.transform(node.a), self.transform(node.b))

    def transform_Less(self, node : Less) -> Less:
        return Less(self.transform(node.a), self.transform(node.b))

    def transform_IndexRange(self, node : IndexRange) -> IndexRange:
        return IndexRange(node.var_name, self.transform(node.start), self.transform(node.end))

    def transform_EqualsCompareRange(self, node : EqualsCompareRange) -> EqualsCompareRange:
        return EqualsCompareRange(node.is_equals, self.transform(node.index_a), self.transform(node.index_b))

    def transform_Exists(self, node : Exists) -> Exists:
        return Exists([self.transform(var) for var in node.var_refs], [self.transform(cond) for cond in node.conds], self.transform(node.pred))

    def transform_VarRef(self, node : VarRef) -> VarRef:
        return node

    def transform_AutLiteral(self, node : AutLiteral) -> AutLiteral:
        return node

    def transform_SpotFormula(self, node : SpotFormula) -> SpotFormula:
        return node

    def transform_Call(self, node : Call) -> Call:
        return Call(node.name, [self.transform(arg) for arg in node.args])

    def transform_PredicateExpr(self, node : PredicateExpr) -> PredicateExpr:
        return PredicateExpr(node.var, self.transform(node.pred)).with_type(node.get_type())

    def transform_NamedPred(self, node : NamedPred) -> NamedPred:
        new_args = [self.transform(arg) for arg in node.args]
        new_restrictions = {self.transform(var): self.transform(restriction) for var, restriction in node.arg_restrictions.items()}
        return NamedPred(node.name, new_args, new_restrictions, self.transform(node.body), restriction_env=node.restriction_env, body_evaluated=node.body_evaluated, arg_name_map=node.arg_name_map)

    def transform_Program(self, node : Program) -> Program:
        self.current_program = Program([]).copy_defaults(node)
        self.current_program.defs = [self.transform(d) for d in node.defs]
        self.current_program.restrictions = [{k: list(map(self.transform, v)) for k, v in restrictions.items()} for restrictions in node.restrictions]
        self.current_program.types = dict([self.transform_type(k, v) for k, v in node.types.items()])
        self.current_program.preds = {k: self.transform(d) for k, d in node.preds.items()}
        self.current_program.praline_defs = {k: self.transform(d) for k, d in node.praline_defs.items()}
        self.current_program.praline_envs = [{k: self.transform(d) for k, d in env} for env in node.praline_envs]
        self.current_program.praline_aliases = {k: self.transform(d) for k, d in node.praline_aliases.items()}
        new_program = self.current_program
        self.current_program = None
        return new_program

    def transform_type(self, pred_ref : VarRef | Call, val_dict : dict[str, Call]) -> tuple[VarRef | Call, dict[str, Call]]:
        return (pred_ref, val_dict)

    def transform_Restriction(self, node : Restriction) -> Restriction:
        return Restriction(list(map(self.transform, node.restrict_vars)), self.transform(node.pred))

    def transform_FunctionExpression(self, node : FunctionExpression) -> FunctionExpression:
        return FunctionExpression(self.transform(node.pred_name), [self.transform(arg) for arg in node.args], node.val_idx).with_type(node.get_type())

    def transform_PralineAlias(self, node : PralineAlias) -> PralineAlias:
        return PralineAlias(self.transform(node.name), self.transform(node.directive_name), self.transform(node.term))

    def transform_PralineDirective(self, node : PralineDirective) -> PralineDirective:
        return PralineDirective(self.transform(node.name), self.transform(node.term))

    def transform_PralineDef(self, node : PralineDef) -> PralineDef:
        return PralineDef(self.transform(node.name), list(map(self.transform, node.args)), self.transform(node.body))

    def transform_PralineApp(self, node : PralineApp) -> PralineApp:
        return PralineApp(self.transform(node.receiver), self.transform(node.arg))

    def transform_PralineAdd(self, node : PralineAdd) -> PralineAdd:
        return PralineAdd(self.transform(node.a), self.transform(node.b))

    def transform_PralineDiv(self, node : PralineDiv) -> PralineDiv:
        return PralineDiv(self.transform(node.a), self.transform(node.b))

    def transform_PralineSub(self, node : PralineSub) -> PralineSub:
        return PralineSub(self.transform(node.a), self.transform(node.b))

    def transform_PralineMul(self, node : PralineMul) -> PralineMul:
        return PralineMul(self.transform(node.a), self.transform(node.b))

    def transform_PralineExponent(self, node : PralineExponent) -> PralineExponent:
        return PralineExponent(self.transform(node.a), self.transform(node.b))

    def transform_PralineNeg(self, node : PralineNeg) -> PralineNeg:
        return PralineNeg(self.transform(node.a))

    def transform_PralineList(self, node : PralineList) -> PralineList:
        return PralineList(self.transform(node.a), self.transform(node.b))

    def transform_PralineMatch(self, node : PralineMatch) -> PralineMatch:
        return PralineMatch(self.transform(node.t), list(map(self.transform, node.arms)))

    def transform_PralineMatchArm(self, node : PralineMatchArm) -> PralineMatchArm:
        return PralineMatchArm(self.transform(node.pat), self.transform(node.expr))

    def transform_PralineMatchInt(self, node : PralineMatchInt) -> PralineMatchInt:
        return PralineMatchInt(node.val)

    def transform_PralineMatchString(self, node : PralineMatchString) -> PralineMatchString:
        return PralineMatchString(self.transform(node.val))

    def transform_PralineMatchList(self, node : PralineMatchList) -> PralineMatchList:
        return PralineMatchList(self.transform(node.head), self.transform(node.tail))

    def transform_PralineMatchTuple(self, node : PralineMatchTuple) -> PralineMatchTuple:
        return PralineMatchTuple([self.transform(v) for v in node.vals])

    def transform_PralineMatchVar(self, node : PralineMatchVar) -> PralineMatchVar:
        return PralineMatchVar(self.transform(node.var))

    def transform_PralineMatchPecan(self, node : PralineMatchPecan) -> PralineMatchPecan:
        return PralineMatchPecan(self.transform(node.pecan_term))

    def transform_PralineIf(self, node : PralineIf) -> PralineIf:
        return PralineIf(self.transform(node.cond), self.transform(node.e1), self.transform(node.e2))

    def transform_PralinePecanTerm(self, node : PralinePecanTerm) -> PralinePecanTerm:
        return PralinePecanTerm(self.transform(node.pecan_term))

    def transform_PralinePecanLiteral(self, node : PralinePecanLiteral) -> PralinePecanLiteral:
        return PralinePecanLiteral(self.transform(node.get_term()))

    def transform_PralineLambda(self, node : PralineLambda) -> PralineLambda:
        return PralineLambda(list(map(self.transform, node.params)), self.transform(node.body))

    def transform_PralineLetPecan(self, node : PralineLetPecan) -> PralineLetPecan:
        return PralineLetPecan(self.transform(node.var_name), self.transform(node.pecan_term), self.transform(node.body))

    def transform_PralineLet(self, node : PralineLet) -> PralineLet:
        return PralineLet(self.transform(node.var_name), self.transform(node.expr), self.transform(node.body))

    def transform_PralineTuple(self, node : PralineTuple) -> PralineTuple:
        return PralineTuple(list(map(self.transform, node.vals)))

    def transform_PralineVar(self, node : PralineVar) -> PralineVar:
        return PralineVar(node.var_name)

    def transform_PralineInt(self, node : PralineInt) -> PralineInt:
        return PralineInt(node.val)

    def transform_PralineString(self, node : PralineString) -> PralineString:
        return PralineString(node.val)

    def transform_PralineBool(self, node : PralineBool) -> PralineBool:
        return PralineBool(node.val)

    def transform_Closure(self, node : Closure) -> Closure:
        new_env = {k: self.transform(v) for k, v in node.env.items()}
        new_args = [self.transform(arg) for arg in node.args]
        new_body = self.transform(node.body)
        return Closure(new_env, new_args, new_body)

    def transform_Builtin(self, node : Builtin) -> Builtin:
        return node

    def transform_PralineDo(self, node : PralineDo) -> PralineDo:
        return PralineDo([self.transform(t) for t in node.terms])

    def transform_PralineAutomaton(self, node : PralineAutomaton) -> PralineAutomaton:
        return node

    def transform_Annotation(self, node : Annotation) -> Annotation:
        return Annotation(node.annotation_name, self.transform(node.body))

    def transform_TypeHint(self, node : TypeHint) -> TypeHint:
        return TypeHint(self.transform(node.expr_a), self.transform(node.expr_b), self.transform(node.body))

