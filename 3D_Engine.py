from var import *



ModelData = load_model("torus.obj")
                       
if __name__ == '__main__':
    p = Screen(width=200, height=70, show_fps=True, font_size=14, obj_scale=30, obj=ModelData)

    p.render()


    
