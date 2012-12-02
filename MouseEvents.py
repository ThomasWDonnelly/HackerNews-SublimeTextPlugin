import sublime
import sublime_plugin

class DragSelectCallbackCommand(sublime_plugin.TextCommand):
    def run_(self, args):
        for c in sublime_plugin.all_callbacks.setdefault('on_pre_mouse_down',[]):
            c.on_pre_mouse_down(args, self.view)

        #We have to make a copy of the selection, otherwise we'll just have
        #a *reference* to the selection which is useless if we're trying to
        #roll back to a previous one. A RegionSet doesn't support slicing so
        #we have a comprehension instead.
        old_sel = [r for r in self.view.sel()]

        #Only send the event so we don't do an extend or subtract or
        #whatever. We want the only selection to be where they clicked.
        self.view.run_command("drag_select", {'event': args['event']})
        new_sel = self.view.sel()
        click_point = new_sel[0].a

        #Restore the old selection so when we call drag_select in will
        #behave normally.
        new_sel.clear()
        map(new_sel.add, old_sel)

        #This is the "real" drag_select that alters the selection for real.
        self.view.run_command("drag_select", args)

        for c in sublime_plugin.all_callbacks.setdefault('on_post_mouse_down',[]):
            c.on_post_mouse_down(click_point, self.view)

class MouseEventListener(sublime_plugin.EventListener):
    sublime_plugin.all_callbacks.setdefault('on_pre_mouse_down', [])
    sublime_plugin.all_callbacks.setdefault('on_post_mouse_down', [])
    
    def __init__(self, view = None):
        self.current_view = view