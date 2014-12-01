import sublime, sublime_plugin
import re

from collections import namedtuple

BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

# House keeping for the async beast
activeChecks = 0
dismissedChecks = 0

# scopeNames is used to avoid a weird memory leak with Sublime Text which occurs
# when calling view.scope_name within an async routine
scopeNames = []


class EventListener(sublime_plugin.EventListener):

  def on_modified(self, view):

    if not self.doAutoCheck(view):
      print("on_modified")
      self.clearRegions(view)
      return

    self.collectScopeNames(view)

    if view.settings().get("is_test", False):
      self.highlightBracketError(view)


  def clearRegions(self, view):

    view.erase_regions("BracketGuardRegions")


  def collectScopeNames(self, view):

    global scopeNames
    scopeNames = [view.scope_name(i) for i in range(len(self.getBufferContent(view)))]


  def on_post_save(self, view):

    if self.checkOnSave() and not self.doAutoCheck(view):
      self.collectScopeNames(view)


  def on_post_save_async(self, view):

    if self.checkOnSave() and not self.doAutoCheck(view):
      self.highlightBracketError(view)


  def checkOnSave(self):

    settings = sublime.load_settings("BracketGuard.sublime-settings")
    return settings.get("check_on_save")


  def doAutoCheck(self, view):

    settings = sublime.load_settings("BracketGuard.sublime-settings")
    threshold = settings.get("file_length_threshold")
    bufferContent = self.getBufferContent(view)
    return threshold >= len(bufferContent)


  def on_modified_async(self, view):

    if not self.doAutoCheck(view):
      return

    self.highlightBracketError(view)


  def highlightBracketError(self, view):

    global activeChecks, dismissedChecks

    if activeChecks > 0:
      dismissedChecks += 1
      return

    bufferContent = self.getBufferContent(view)

    activeChecks += 1
    bracketResult = getFirstBracketError(bufferContent, view)

    if dismissedChecks > 0:
      dismissedChecks = 0
      bracketResult = getFirstBracketError(bufferContent, view)

    activeChecks -= 1

    if bracketResult.success:
      view.erase_regions("BracketGuardRegions")
    else:
      openerRegion = sublime.Region(bracketResult.start, bracketResult.start + 1)
      closerRegion = sublime.Region(bracketResult.end, bracketResult.end + 1)
      view.add_regions("BracketGuardRegions", [openerRegion, closerRegion], "invalid")


  def getBufferContent(self, view):

    contentRegion = sublime.Region(0, view.size())
    return view.substr(contentRegion)



def getFirstBracketError(codeStr, view):
  global scopeNames, dismissedChecks

  opener = list("({[")
  closer = list(")}]")

  matchingStack = []
  successResult = BracketResult(True, -1, -1)

  for index, char in enumerate(codeStr):

    if dismissedChecks > 0:
      # we will have to start over
      return successResult

    if len(scopeNames) <= index:
      dismissedChecks += 1
      return successResult

    scopeName = scopeNames[index]

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
