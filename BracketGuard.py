import sublime, sublime_plugin
import re

from collections import namedtuple
from timeit import default_timer as timer


BracketPosition = namedtuple("BracketPosition", "position opener")
BracketResult = namedtuple("BracketResult", "success start end")

class SelectionListener(sublime_plugin.EventListener):

  def on_modified(self, view):

    contentRegion = sublime.Region(0, view.size())
    bufferContent = view.substr(contentRegion)

    # start = timer()
    bracketResult = getFirstBracketError(bufferContent, view)
    # end = timer()
    # TODO: check large files only when the user requests it explicitly


    if bracketResult.success:
      view.erase_regions("BracketGuardRegions")
    else:
      openerRegion = sublime.Region(bracketResult.start, bracketResult.start + 1)
      closerRegion = sublime.Region(bracketResult.end, bracketResult.end + 1)
      view.add_regions("BracketGuardRegions", [openerRegion, closerRegion], "invalid")


def getFirstBracketError(codeStr, view):

  opener = list("({[")
  closer = list(")}]")

  matchingStack = []

  for index, char in enumerate(codeStr):

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
    return BracketResult(True, -1, -1)
  else:
    poppedOpener = matchingStack.pop()
    return BracketResult(False, poppedOpener.position, len(codeStr) - 1)
