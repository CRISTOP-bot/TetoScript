import unittest
from tetoscript.lexer import TetoSyntaxError
from tetoscript.runtime import TetoRuntimeError, run
from tetoscript.__main__ import main
from tetoscript.checker import TetoCheckError, check
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile

class InterpreterTests(unittest.TestCase):
    def test_example_functions_types_modulo_and_branches(self):
        source='''teto name: string = "Teto"
teto age: number = 25
teto fn greet(person: string) -> string { return "Hello " + person }
Teto (age % 2 == 1) { tetolog(greet(name)) } else { tetolog("nose") }'''
        self.assertEqual(run(source),["Hello Teto"])
    def test_else_branch_and_null_spelling(self):
        self.assertEqual(run('Teto (false) { tetolog("yes") } else { tetolog(nose) }'),["nose"])
    def test_type_annotation_rejects_wrong_type(self):
        with self.assertRaisesRegex(TetoRuntimeError,"se esperaba number"):
            run('teto age: number = "25"')
    def test_function_argument_type_is_checked(self):
        with self.assertRaisesRegex(TetoRuntimeError,"se esperaba string"):
            run('teto fn greet(name: string) -> string { return name } tetolog(greet(25))')
    def test_undefined_name_reports_error(self):
        with self.assertRaisesRegex(TetoRuntimeError,"variable no definida"):
            run('tetolog(ghost)')
    def test_rejects_unknown_character(self):
        with self.assertRaises(TetoSyntaxError): run('tetolog(@)')
    def test_rejects_duplicate_declaration(self):
        with self.assertRaisesRegex(TetoRuntimeError,"ya declarada"):
            run('teto x = 1 teto x = 2')
    def test_precedence_and_short_circuit(self):
        self.assertEqual(run('tetolog(2 + 3 * 4) tetolog(false and ghost)'),["14","false"])
    def test_non_callable_error(self):
        with self.assertRaisesRegex(TetoRuntimeError,"no se puede llamar"):
            run('teto x = 2 x()')
    def test_check_command_does_not_execute_program(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"check.teto"
            path.write_text('tetolog("this must not print")',encoding="utf-8")
            out=StringIO()
            with redirect_stdout(out): self.assertEqual(main(["check",str(path)]),0)
            self.assertIn("Análisis correcto",out.getvalue())
            self.assertNotIn("this must not print",out.getvalue())
    def test_check_command_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"broken.teto"
            path.write_text('Teto (true) {',encoding="utf-8")
            err=StringIO()
            with redirect_stderr(err): self.assertEqual(main(["check",str(path)]),1)
            self.assertIn("TetoScript:",err.getvalue())
    def test_static_checker_rejects_undefined_name(self):
        with self.assertRaisesRegex(TetoCheckError,"nombre no definido: phantom"):
            check('tetolog(phantom)')
    def test_static_checker_rejects_wrong_variable_type(self):
        with self.assertRaisesRegex(TetoCheckError,"se esperaba number, se obtuvo string"):
            check('teto age: number = "25"')
    def test_static_checker_rejects_wrong_function_argument(self):
        source='teto fn greet(name: string) -> string { return name } tetolog(greet(25))'
        with self.assertRaisesRegex(TetoCheckError,"argumento 1 de greet: se esperaba string"):
            check(source)
    def test_static_checker_accepts_complete_example(self):
        check(Path("examples/hello.teto").read_text(encoding="utf-8"))
    def test_static_checker_rejects_return_outside_function(self):
        with self.assertRaisesRegex(TetoCheckError,"return solo se permite"):
            check('return 5')
    def test_check_command_finds_semantic_error_without_running(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"bad.teto"
            path.write_text('tetolog(notDefined)',encoding="utf-8")
            err=StringIO()
            with redirect_stderr(err): self.assertEqual(main(["check",str(path)]),1)
            self.assertIn("nombre no definido: notDefined",err.getvalue())
    def test_static_checker_rejects_wrong_function_return(self):
        with self.assertRaisesRegex(TetoCheckError,"valor de retorno: se esperaba number"):
            check('teto fn count() -> number { return "five" }')
    def test_static_checker_rejects_non_boolean_condition(self):
        with self.assertRaisesRegex(TetoCheckError,"condición de Teto: se esperaba boolean"):
            check('Teto (5) { tetolog("yes") }')
    def test_assignment_and_while_loop(self):
        source='''teto i: number = 0
teto total: number = 0
while (i < 5) {
    total = total + i
    i = i + 1
}
tetolog(total)'''
        check(source)
        self.assertEqual(run(source),["10"])
    def test_static_checker_rejects_bad_assignment_type(self):
        with self.assertRaisesRegex(TetoCheckError,"reasignación de age: se esperaba number"):
            check('teto age: number = 25 age = "old"')
    def test_static_checker_rejects_assignment_to_unknown_name(self):
        with self.assertRaisesRegex(TetoCheckError,"nombre no definido: ghost"):
            check('ghost = 5')
    def test_runtime_rejects_bad_assignment_type(self):
        with self.assertRaisesRegex(TetoRuntimeError,"se esperaba number"):
            run('teto age: number = 25 age = "old"')
    def test_runtime_stops_non_terminating_loop(self):
        with self.assertRaisesRegex(TetoRuntimeError,"100000 iteraciones"):
            run('while (true) {}')
    def test_checker_rejects_reassigning_function(self):
        with self.assertRaisesRegex(TetoCheckError,"no se puede reasignar la función"):
            check('teto fn f() -> number { return 1 } f = 2')

if __name__=="__main__": unittest.main()
