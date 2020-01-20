import bpy
from ..utils import validMaxMinRGB, valid_video_layer, valid_image_layer, colorDivision, truncate_name

class SM_OT_color_balance_node(bpy.types.Operator):
    bl_idname = 'shot_matcher.color_balance_node'
    bl_label = 'Shot Matcher: Color Balance'
    bl_description = 'Creates a color balance node that maps the max/min values from the foreground to the background layer'
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls, context):
        bg_layer = context.scene.sm_background
        fg_layer = context.scene.sm_foreground

        bg_valid = (bg_layer.layer_type == 'video' and valid_video_layer(bg_layer)) or valid_image_layer(bg_layer)
        fg_valid = (fg_layer.layer_type == 'video' and valid_video_layer(fg_layer)) or valid_image_layer(fg_layer)

        return bg_valid and fg_valid
    
    def execute(self, context):
        bg_layer = context.scene.sm_background
        fg_layer = context.scene.sm_foreground
        node_name = 'CB: ' + truncate_name(fg_layer.layer_name, 12) + ' -> ' + truncate_name(bg_layer.layer_name, 12)
        context.scene.use_nodes = True
      
        if validMaxMinRGB(context) is False:
            self.report({'ERROR'}, 'The white color is less than or equal to the black color')
            return {'FINISHED'}
        
        tree = context.scene.node_tree
        cb_node = next((node for node in tree.nodes if node.label == node_name), None)
        
        if cb_node is None:    
            #create color balance node
            cb_node = tree.nodes.new(type='CompositorNodeColorBalance')              
            cb_node.correction_method = 'OFFSET_POWER_SLOPE'
            cb_node.label = node_name

        bg_slope = bg_layer.max_color - bg_layer.min_color
        fg_slope = fg_layer.max_color - fg_layer.min_color
        try:
            cb_node.slope = colorDivision(bg_slope, fg_slope)
        except:
            self.report({'ERROR'}, 'Failed: division by zero ([foreground white color] - [foreground black color] must not equal zero!)')
            return {'FINISHED'}
        cb_node.offset = bg_layer.min_color - fg_layer.min_color
                
        return {'FINISHED'}
