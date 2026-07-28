#!/usr/bin/env python3.6
# -*- coding=utf-8 -*-

import time

from pecan.tools.shuffle_automata import ShuffleAutomata
from pecan.tools.walnut_converter import convert_aut
from pecan.tools.hoa_loader import load_hoa
from pecan.tools.labeled_aut_converter import convert_labeled_aut
from pecan.tools.hoa_loader import load_hoa
from pecan.tools.finite_loader import load_finite
from pecan.automata.buchi import BuchiAutomaton
from pecan.lang.ir import *

from pecan.logger import Logger

from pecan.lang.ir.base import IRNode
from pecan.lang.ir.prog import AutLiteral, Call, NamedPred, Program, Result

from typing import TYPE_CHECKING
if TYPE_CHECKING :
    from typing import Any, Literal
    from pecan.lang.ir_transformer import IRTransformer
    from pecan.lang.type_inference import RestrictionType
    from pecan.lang.ir.prog import Program

class DirectiveIRNode(IRNode):
    def __init__(self):
        super().__init__()
    
    def evaluate(self, prog: Program) -> None | Result:
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return self.__str__()

class DirectiveSaveAut(DirectiveIRNode):
    def __init__(self, filename : str, pred_name : str):
        super().__init__()
        self.filename : str = filename
        self.pred_name : str = pred_name

    def evaluate(self, prog : Program) -> None:
        Logger.info('Saving {} as {}'.format(self.pred_name, self.filename))

        prog.add_generated_file(self.filename)

        prog.call(self.pred_name).aut.save(self.filename)
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveSaveAut:
        return transformer.transform_DirectiveSaveAut(self)

    def __str__(self) -> str:
        return '#save_aut({}, {})'.format(str(self.filename), self.pred_name)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.filename == other.filename and self.pred_name == other.pred_name

    def __hash__(self) -> int:
        return hash((self.filename, self.pred_name))

class DirectiveSaveAutImage(DirectiveIRNode):
    def __init__(self, filename : str, pred_name : str):
        super().__init__()
        self.filename : str = filename
        self.pred_name : str = pred_name

    def evaluate(self, prog : Program) -> None:
        # TODO: Support formats other than SVG?
        Logger.info('Saving {} as an SVG in {}'.format(self.pred_name, self.filename))

        evaluated = BuchiAutomaton.as_buchi(prog.call(self.pred_name).aut)
        with open(self.filename, 'wb') as f:
            f.write(evaluated.show().data.encode('utf-8')) # Write the raw svg data into the file

        prog.add_generated_file(self.filename)

        return None

    def transform(self, transformer : IRTransformer) -> DirectiveSaveAutImage:
        return transformer.transform_DirectiveSaveAutImage(self)

    def __str__(self) -> str:
        return '#save_aut_img({}, {})'.format(str(self.filename), self.pred_name)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.filename == other.filename and self.pred_name == other.pred_name

    def __hash__(self) -> int:
        return hash((self.filename, self.pred_name))

class DirectiveContext(DirectiveIRNode):
    def __init__(self, context_key : str, context_val : str):
        super().__init__()
        self.context_key : str = context_key
        self.context_val : str = context_val

    def evaluate(self, prog : Program) -> None:
        prog.context[self.context_key] = self.context_val
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveContext:
        return transformer.transform_DirectiveContext(self)

    def __str__(self) -> str:
        return '#context({}, {})'.format(self.context_key, self.context_val)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.context_key == other.context_key and self.context_val == other.context_val

    def __hash__(self) -> int:
        return hash((self.context_key, self.context_val))

class DirectiveEndContext(DirectiveIRNode):
    def __init__(self, context_key : str):
        super().__init__()
        self.context_key : str = context_key

    def evaluate(self, prog : Program) -> None:
        prog.context.pop(self.context_key)
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveEndContext:
        return transformer.transform_DirectiveEndContext(self)

    def __str__(self) -> str:
        return '#end_context({})'.format(self.context_key)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.context_key == other.context_key

    def __hash__(self) -> int:
        return hash(self.context_key)

# Asserts that pred_name is truth_val: i.e., that pred_name is 'true' (always), 'false' (always), or 'sometimes' true
class DirectiveAssertProp(DirectiveIRNode):
    def __init__(self, truth_val : Literal['false', 'true', 'sometimes'], pred_name : str):
        super().__init__()
        self.truth_val : Literal['false', 'true', 'sometimes'] = truth_val
        self.pred_name : str = pred_name

    def pred_truth_value(self, prog : Program) -> Literal['false', 'true', 'sometimes']:
        return Call(self.pred_name, []).evaluate(prog).truth_value()

    def evaluate(self, prog : Program) -> Result:
        Logger.info('Checking if {} is {}.'.format(self.pred_name, self.display_truth_val()))

        pred_truth_value = self.pred_truth_value(prog)

        if pred_truth_value == self.truth_val:
            result = Result('{} is {}.'.format(self.pred_name, self.display_truth_val()), True)
        else:
            result = Result('{} is not {}.'.format(self.pred_name, self.display_truth_val()), False)

        Logger.log(result.result_str())

        return result

    def transform(self, transformer : IRTransformer) -> DirectiveAssertProp:
        return transformer.transform_DirectiveAssertProp(self)

    def display_truth_val(self) -> Literal['false', 'true', 'sometimes true']:
        if self.truth_val == 'sometimes':
            return 'sometimes true'
        else:
            return self.truth_val # 'true' or 'false'

    def __str__(self) -> str:
        return '#assert_prop({}, {})'.format(self.truth_val, self.pred_name)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and self.truth_val == other.truth_val and self.pred_name == other.pred_name

    def __hash__(self) -> int:
        return hash((self.truth_val, self.pred_name))

class DirectiveLoadAut(DirectiveIRNode):
    def __init__(self, filename : str, aut_format : str, pred : Call):
        super().__init__()
        self.filename : str = filename
        self.aut_format : str = aut_format
        self.pred : Call = pred

    def evaluate(self, prog : Program) -> None:
        # TODO: Support argument restrictions on loaded automata
        start_time = time.time()
        realpath = prog.locate_file(self.filename)
        Logger.info('Loading {} from {} in "{}" format.'.format(self.pred, realpath, self.aut_format), 0, True)

        if self.aut_format == 'hoa':
            # TODO: Rename the APs of the loaded automaton to be the same as the args specified
            aut = load_hoa(realpath)
        elif self.aut_format == 'walnut':
            aut = convert_aut(realpath, [v.var_name for v in self.pred.args])
        elif self.aut_format == 'pecan':
            aut = convert_labeled_aut(realpath, [v.var_name for v in self.pred.args])
        elif self.aut_format == 'fsa-dict':
            aut = load_finite(realpath, [v.var_name for v in self.pred.args])
        else:
            raise KeyError('Unknown format: {}'.format(self.aut_format))

        end_time = time.time()

        Logger.info('Loaded {} in {:.2f} seconds ({} states, {} edges).'.format(self.pred, end_time - start_time, aut.num_states(), aut.num_edges()), 0)

        prog.preds[self.pred.name] = NamedPred(self.pred.name, self.pred.args, {}, AutLiteral(aut))

        return None

    def transform(self, transformer : IRTransformer) -> DirectiveLoadAut:
        return transformer.transform_DirectiveLoadAut(self)

    def __str__(self) -> str:
        return '#load({}, {}, {})'.format(self.filename, self.aut_format, str(self.pred))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and \
               self.filename == other.filename and self.aut_format == other.aut_format and self.pred == other.pred

    def __hash__(self) -> int:
        return hash((self.filename, self.aut_format, self.pred))

class DirectiveImport(DirectiveIRNode):
    def __init__(self, filename : str):
        super().__init__()
        self.filename : str = filename

    def evaluate(self, prog : Program) -> None:
        realpath = prog.locate_file(self.filename)
        from pecan.program import load
        new_prog = load(realpath).copy_defaults(prog)
        new_prog.evaluate_prog()
        prog.include(new_prog)
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveImport:
        return transformer.transform_DirectiveImport(self)

    def __str__(self) -> str:
        return '#import({})'.format(str(self.filename))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and \
               self.filename == other.filename

    def __hash__(self) -> int:
        return hash(self.filename)

class DirectiveForget(DirectiveIRNode):
    def __init__(self, var_name : str):
        super().__init__()
        self.var_name : str = var_name

    def evaluate(self, prog : Program) -> None:
        prog.forget_global(self.var_name)
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveForget:
        return transformer.transform_DirectiveForget(self)

    def __str__(self) -> str:
        return '#forget({})'.format(str(self.var_name))

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and \
               self.var_name == other.var_name

    def __hash__(self) -> int:
        return hash(self.var_name)

class DirectiveStructure(DirectiveIRNode):
    def __init__(self, pred_ref : RestrictionType, val_dict : dict[str, Call]):
        super().__init__()
        self.pred_ref : RestrictionType = pred_ref
        self.val_dict : dict[str, Call] = val_dict

    def evaluate(self, prog : Program) -> None:
        prog.declare_type(self.pred_ref, self.val_dict)
        return None

    def transform(self, transformer : IRTransformer) -> DirectiveStructure:
        return transformer.transform_DirectiveStructure(self)

    def __str__(self) -> str:
        return 'Structure {} defining {}.'.format(self.pred_ref, self.val_dict)

    def __eq__(self, other : Any) -> bool:
        return other is not None and isinstance(other, self.__class__) and \
               self.pred_ref == other.pred_ref and self.val_dict == other.val_dict

    def __hash__(self) -> int:
        return hash((self.pred_ref, self.val_dict))

class DirectiveShuffle(DirectiveIRNode):
    def __init__(self, disjunction : bool, pred_a : Call, pred_b : Call, output_pred : Call):
        super().__init__()
        self.disjunction : bool = disjunction
        self.pred_a : Call = pred_a
        self.pred_b : Call = pred_b
        self.output_pred : Call = output_pred

    def transform(self, transformer : IRTransformer) -> DirectiveShuffle:
        return transformer.transform_DirectiveShuffle(self)

    def evaluate(self, prog : Program) -> None:
        # TODO: Support shuffling other kinds of automata, once we have them
        a_aut = BuchiAutomaton.as_buchi(prog.call(self.pred_a.name, self.pred_a.args).aut)
        b_aut = BuchiAutomaton.as_buchi(prog.call(self.pred_b.name, self.pred_b.args).aut)

        res = a_aut.shuffle(self.disjunction, b_aut)

        prog.preds[self.output_pred.name] = NamedPred(self.output_pred.name, self.output_pred.args, {}, AutLiteral(res))

        return None

    def __str__(self) -> str:
        return '#shuffle({}, {}, {})'.format(self.pred_a, self.pred_b, self.output_pred)
