from var import *



ModelData = load_model("cube.obj")
                       
if __name__ == '__main__':
    p = Screen(width=200, height=70, font_size=14, obj_scale=20, obj=ModelData)

    p.render()


    
