import bpy
from ..LayerSettings import LayerSettings
from ..utils import get_layer_settings

class SM_OT_color_picker(bpy.types.Operator):
    bl_idname = 'shot_matcher.color_picker'
    bl_description = 'Use a color picker to select the white and black values'
    bl_label = 'Min Max Color Picker'
    
    @classmethod
    def poll(cls, context):
        return context.edit_image is not None and context.edit_image.pixels

    def modal(self, context, event):
        
        context.window.cursor_set('EYEDROPPER')   
    
        context.area.header_text_set(text='Ctrl + Mouse: pick white/black colors, LMB/RMB: finish and apply, ESC: cancel')
        
        if event.type == 'MOUSEMOVE':
            if event.ctrl:
                mouse_x = event.mouse_x - context.region.x
                mouse_y = event.mouse_y - context.region.y
                uv = context.area.regions[-1].view2d.region_to_view(mouse_x, mouse_y)
                img = context.edit_image
                size_x, size_y = img.size[:]
                x = int(size_x * uv[0]) % size_x
                y = int(size_y * uv[1]) % size_y
                offset = (y * size_x + x) * 4
                pixels = img.pixels[offset:offset+3]
                #check max for each channel
                if pixels[0] > self.max_r:
                    self.max_r = pixels[0]
                if pixels[1] > self.max_g:
                    self.max_g = pixels[1]
                if pixels[2] > self.max_b:
                    self.max_b = pixels[2]                
                #check min for each channel
                if pixels[0] < self.min_r:
                    self.min_r = pixels[0]
                if pixels[1] < self.min_g:
                    self.min_g = pixels[1]
                if pixels[2] < self.min_b:
                    self.min_b = pixels[2]        
        elif event.type in {'RIGHTMOUSE', 'LEFTMOUSE'}:
            context_layer = get_layer_settings(context)
            context_layer.min_color = (self.min_r, self.min_g, self.min_b)
            context_layer.max_color = (self.max_r, self.max_g, self.max_b)
            context.area.header_text_set(text=None)
            context.area.tag_redraw()
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}
        elif event.type == 'ESC':
            context.window.cursor_set('DEFAULT')
            context.area.header_text_set(text=None)
            return {'FINISHED'}
        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context_layer = get_layer_settings(context)
        self.min_r = context_layer.min_color[0]
        self.min_g = context_layer.min_color[1]
        self.min_b = context_layer.min_color[2]
        self.max_r = context_layer.max_color[0]
        self.max_g = context_layer.max_color[1]
        self.max_b = context_layer.max_color[2]
        
        if context.area.type == 'IMAGE_EDITOR' and context.edit_image is not None:
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, 'UV/Image Editor not found, cannot run operator')
            return {'CANCELLED'}
