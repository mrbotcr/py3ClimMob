from climmob.products.climmob_products import createProductDirectory,registerProductInstance
from .celerytasks import createDataDesk

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_data_desk(request,user,project, data, name):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request,user,project,'datadesk')
    # We call the Celery task that will generate the output packages.pdf
    task = createDataDesk.delay(path,  name, data)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    registerProductInstance(user,project,'datadesk',name+'.json','application/json','data_desk',task.id,request)