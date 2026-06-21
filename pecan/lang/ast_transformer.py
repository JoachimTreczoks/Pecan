#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

from pecan.lang.ast import *

class AstTransformer:
    def __init__(self):
        pass

    def transform[T : ASTNode](self, node : T) -> T:
        if node is None:
            return None
        elif type(node) is str:
            return self.transform_str(node)
        else:
            return node.transform(self)

    def transform_str(self, node : str) -> str:
        return node
    
    def transform_truth_value(self, node : Literal['false', 'true', 'sometimes']) -> Literal['false', 'true', 'sometimes']:
        return node

    def transform_Conjunction(self, node : Conjunction) -> Conjunction:
        return Conjunction(self.transform(node.a), self.transform(node.b))

    def transform_Disjunction(self, node : Disjunction) -> Disjunction:
        return Disjunction(self.transform(node.a), self.transform(node.b))

    def transform_Complement(self, node : Complement) -> Complement:
        return Complement(self.transform(node.a))

    def transform_Iff(self, node : Iff) -> Iff:
        return Iff(self.transform(node.a), self.transform(node.b))

    def transform_Implies(self, node : Implies) -> Implies:
        return Implies(self.transform(node.a), self.transform(node.b))

    def transform_BoolConst(self, node : BoolConst) -> BoolConst:
        return node

    def transform_DirectiveSaveAut(self, node : DirectiveSaveAut) -> DirectiveSaveAut:
        return DirectiveSaveAut(self.transform_str(node.filename), self.transform_str(node.pred_name))

    def transform_DirectiveSaveAutImage(self, node : DirectiveSaveAutImage) -> DirectiveSaveAutImage:
        return DirectiveSaveAutImage(self.transform_str(node.filename), self.transform_str(node.pred_name))

    def transform_DirectiveContext(self, node : DirectiveContext) -> DirectiveContext:
        return DirectiveContext(self.transform_str(node.context_key), self.transform_str(node.context_val))

    def transform_DirectiveEndContext(self, node : DirectiveEndContext) -> DirectiveEndContext:
        return DirectiveEndContext(self.transform_str(node.context_key))

    def transform_DirectiveAssertProp(self, node : DirectiveAssertProp) -> DirectiveAssertProp:
        return DirectiveAssertProp(self.transform_truth_value(node.truth_val), self.transform_str(node.pred_name))

    def transform_DirectiveLoadAut(self, node : DirectiveLoadAut) -> DirectiveLoadAut:
        return DirectiveLoadAut(self.transform_str(node.filename), self.transform_str(node.aut_format), self.transform(node.pred))

    def transform_DirectiveImport(self, node : DirectiveImport) -> DirectiveImport:
        return DirectiveImport(self.transform_str(node.filename))

    def transform_DirectiveForget(self, node : DirectiveForget) -> DirectiveForget:
        return DirectiveForget(self.transform_str(node.var_name))

    def transform_DirectiveStructure(self, node : DirectiveStructure) -> DirectiveStructure:
        return DirectiveStructure(self.transform(node.pred_ref),
                {self.transform_str(k): self.transform(v) for k, v in node.val_dict.items()})

    def transform_DirectiveShuffle(self, node : DirectiveShuffle) -> DirectiveShuffle:
        return DirectiveShuffle(node.disjunction, self.transform(node.pred_a), self.transform(node.pred_b), self.transform(node.output_pred))

    def transform_Add(self, node : Add) -> Add:
        return Add(self.transform(node.a), self.transform(node.b))

    def transform_Sub(self, node : Sub) -> Sub:
        return Sub(self.transform(node.a), self.transform(node.b))

    def transform_Mul(self, node : Mul) -> Mul:
        return Mul(self.transform(node.a), self.transform(node.b))

    def transform_Div(self, node : Div) -> Div:
        return Div(self.transform(node.a), self.transform(node.b))

    def transform_IntConst(self, node : IntConst) -> IntConst:
        return node

    def transform_Equals(self, node : Equals) -> Equals:
        return Equals(self.transform(node.a), self.transform(node.b))

    def transform_NotEquals(self, node : NotEquals) -> NotEquals:
        return NotEquals(self.transform(node.a), self.transform(node.b))

    def transform_Less(self, node : Less) -> Less:
        return Less(self.transform(node.a), self.transform(node.b))

    def transform_Greater(self, node : Greater) -> Greater:
        return Greater(self.transform(node.a), self.transform(node.b))

    def transform_LessEquals(self, node : LessEquals) -> LessEquals:
        return LessEquals(self.transform(node.a), self.transform(node.b))

    def transform_GreaterEquals(self, node : GreaterEquals) -> GreaterEquals:
        return GreaterEquals(self.transform(node.a), self.transform(node.b))

    def transform_Neg(self, node : Neg) -> Neg:
        return Neg(self.transform(node.a))

    def transform_Index(self, node : Index) -> Index:
        return Index(node.var_name, self.transform(node.index_expr))

    def transform_IndexRange(self, node : IndexRange) -> IndexRange:
        return IndexRange(node.var_name, self.transform(node.start), self.transform(node.end))

    def transform_EqualsCompareIndex(self, node : EqualsCompareIndex) -> EqualsCompareIndex:
        return EqualsCompareIndex(node.is_equals, self.transform_Index(node.index_a), self.transform(node.index_b))

    def transform_EqualsCompareRange(self, node : EqualsCompareRange) -> EqualsCompareRange:
        return EqualsCompareRange(node.is_equals, self.transform_IndexRange(node.index_a), self.transform_IndexRange(node.index_b))

    def transform_Forall(self, node: Forall) -> Forall:
        return Forall([self.transform(var_pred) for var_pred in node.var_preds], self.transform(node.pred))

    def transform_Exists(self, node: Exists) -> Exists:
        return Exists([self.transform(var_pred) for var_pred in node.var_preds], self.transform(node.pred))

    def transform_VarRef(self, node: VarRef) -> VarRef:
        return node

    def transform_AutLiteral(self, node : AutLiteral) -> AutLiteral:
        return node

    def transform_SpotFormula(self, node : SpotFormula) -> SpotFormula:
        return node

    def transform_Call(self, node : Call) -> Call:
        return Call(node.name, [self.transform(arg) for arg in node.args])

    def transformExpr(self, node : PredicateExpr) -> PredicateExpr:
        return PredicateExpr(self.transform_str(node.var_name), self.transform_TypeHint(node.pred))

    def transform_NamedPred(self, node : NamedPred) -> NamedPred:
        return NamedPred(node.name, list(map(self.transform, node.args)), self.transform(node.body))

    def transform_Program(self, node : Program) -> Program:
        new_defs = [self.transform(d) for d in node.defs]
        new_restrictions = [{k: list(map(self.transform, v)) for k, v in restrictions.items()} for restrictions in node.restrictions]
        new_types = dict([self.transform_type(k, v) for k, v in node.types.items()])

        return Program(new_defs, restrictions=new_restrictions, types=new_types).copy_defaults(node)

    def transform_type(self, pred_ref : VarRef | Call, val_dict : dict[str, Call]) -> tuple[VarRef | Call, dict[str, Call]]:
        return (pred_ref, val_dict)

    def transform_Restriction(self, node : Restriction) -> Restriction:
        return Restriction(list(map(self.transform, node.restrict_vars)), self.transform(node.pred))

    def transform_PralineAlias(self, node : PralineAlias) -> PralineAlias:
        return PralineAlias(self.transform_str(node.name), self.transform_str(node.directive_name), self.transform(node.term))

    def transform_PralineDirective(self, node : PralineDirective) -> PralineDirective:
        return PralineDirective(self.transform_str(node.name), self.transform(node.term))

    def transform_PralineDef(self, node : PralineDef) -> PralineDef:
        return PralineDef(reduce(PralineApp, [self.transform_str(node.name)] + list(map(self.transform, node.args))), self.transform(node.body))

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
        return PralineList(self.transform(node.head), self.transform(node.tail))

    def transform_PralineMatch(self, node : PralineMatch) -> PralineMatch:
        return PralineMatch(self.transform(node.t), list(map(self.transform, node.arms)))

    def transform_PralineMatchArm(self, node : PralineMatchArm) -> PralineMatchArm:
        return PralineMatchArm(self.transform(node.pat), self.transform(node.expr))

    def transform_PralineMatchInt(self, node : PralineMatchInt) -> PralineMatchInt:
        return PralineMatchInt(node.val)

    def transform_PralineMatchString(self, node : PralineMatchString) -> PralineMatchString:
        return PralineMatchString(self.transform_str(node.val))

    def transform_PralineMatchList(self, node : PralineMatchList) -> PralineMatchList:
        return PralineMatchList(self.transform(node.head), self.transform(node.tail))

    def transform_PralineMatchTuple(self, node : PralineMatchTuple) -> PralineMatchTuple:
        return PralineMatchTuple([self.transform(v) for v in node.vals])

    def transform_PralineMatchVar(self, node : PralineMatchVar) -> PralineMatchVar:
        return PralineMatchVar(self.transform_str(node.var))

    def transform_PralineMatchPecan(self, node : PralineMatchPecan) -> PralineMatchPecan:
        return PralineMatchPecan(self.transform(node.pecan_term))

    def transform_PralineIf(self, node : PralineIf) -> PralineIf:
        return PralineIf(self.transform(node.cond), self.transform(node.e1), self.transform(node.e2))

    def transform_PralinePecanTerm(self, node : PralinePecanTerm) -> PralinePecanTerm:
        return PralinePecanTerm(self.transform(node.pecan_term))

    def transform_PralineLambda(self, node : PralineLambda) -> PralineLambda:
        return PralineLambda(reduce(PralineApp, list(map(self.transform, node.params))), self.transform(node.body))

    def transform_PralineLetPecan(self, node : PralineLetPecan) -> PralineLetPecan:
        return PralineLetPecan(self.transform_str(node.var_name), self.transform(node.pecan_term), self.transform(node.body))

    def transform_PralineLet(self, node : PralineLet) -> PralineLet:
        return PralineLet(self.transform_str(node.var_name), self.transform(node.expr), self.transform(node.body))

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

    def transform_PralineDo(self, node : PralineDo) -> PralineDo:
        return PralineDo([self.transform(t) for t in node.terms])

    def transform_Annotation(self, node : Annotation) -> Annotation:
        return Annotation(node.annotation_name, self.transform(node.body))

    def transform_TypeHint(self, node : TypeHint) -> TypeHint:
        return TypeHint(self.transform(node.expr_a), self.transform(node.expr_b), self.transform(node.body))

