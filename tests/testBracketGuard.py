import sublime
from unittest import TestCase

version = sublime.version()

class TestBracketGuard(TestCase):

	def setUp(self):

		self.view = sublime.active_window().new_file()


	def tearDown(self):

		if self.view:
			self.view.set_scratch(True)
			self.view.window().run_command("close_file")


	def testValidBrackets(self):

		testString = "([{}])"
		self.view.run_command("insert", {"characters": testString})
		openerRegions = self.view.get_regions("BracketGuardOpenerRegion")

		self.assertEqual(len(openerRegions), 0)


	def testInvalidBrackets(self):

		testString = "({}])"
		self.view.run_command("insert", {"characters": testString})
		bracketGuardRegions = self.view.get_regions("BracketGuardRegions")

		self.assertEqual(len(bracketGuardRegions), 2)
		self.assertEqual(bracketGuardRegions[0].a, 0)
		self.assertEqual(bracketGuardRegions[1].a, 3)
