import sublime, sublime_plugin
import re

from collections import namedtuple

BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

bracketGuardRegions = "BracketGuardRegions"

class EventListener(sublime_plugin.EventListener):

  def on_modified(self, view):

    if view.settings().get("is_test", False):
      self.highlightBracketError(view)


  def on_modified_async(self, view):

    self.clearRegions(view)
    if self.doAutoCheck(view):
       self.highlightBracketError(view)


  def on_post_save_async(self, view):

    if self.checkOnSave() and not self.doAutoCheck(view):
      self.highlightBracketError(view)


  def clearRegions(self, view):

    view.erase_regions(bracketGuardRegions)


  def checkOnSave(self):

    settings = sublime.load_settings("BracketGuard.sublime-settings")
    return settings.get("check_on_save")


  def doAutoCheck(self, view):

    settings = sublime.load_settings("BracketGuard.sublime-settings")
    threshold = settings.get("file_length_threshold")
    return threshold == -1 or threshold >= view.size()


  def highlightBracketError(self, view):

    bracketResult = self.getFirstBracketError(view)

    if not bracketResult.success:
      openerRegion = sublime.Region(bracketResult.start, bracketResult.start + 1)
      closerRegion = sublime.Region(bracketResult.end, bracketResult.end + 1)
      view.add_regions(bracketGuardRegions, [openerRegion, closerRegion], "invalid")


  def getFirstBracketError(view):

    opener = list("({[")
    closer = list(")}]")

    matchingStack = []
    successResult = BracketResult(True, -1, -1)
    codeStr = view.substr(sublime.Region(0, view.size()))

    for index, char in enumerate(codeStr):

      if len(codeStr ) != view.size():
        return successResult

      if char not in opener and not char in closer:
        continue

      scopeName = view.scope_name(index)
      if "string" in scopeName or "comment" in scopeName:
        # ignore unmatched brackets in strings and comments
        continue

      if char in opener:
        matchingStack.append(BracketPosition(index, char))
      elif char in closer:
        matchingOpener = opener[closer.index(char)]

        if len(matchingStack) == 0:
          return BracketResult(False, -1, index)

        poppedOpener = matchingStack.pop()
        if matchingOpener != poppedOpener.opener:
          return BracketResult(False, poppedOpener.position, index)


    if len(matchingStack) == 0:
      return successResult
    else:
      poppedOpener = matchingStack.pop()
      return BracketResult(False, poppedOpener.position, -1)
