from climmob.products.climmob_products import createProductDirectory,registerProductInstance
#from views import myPublicView,myPrivateView
from .celerytasks import createColors



# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_colors_cards(request,user,project,packages):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request,user,project,'colors')
    # We call the Celery task that will generate the output packages.pdf
    print ("*****create_qr_packages. Calling createQR.delay ")
    task = createColors.delay(path,project,packages)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    print ("*****create_qr_packages. registerProductInstance ")
    registerProductInstance(user,project,'colors','colors_'+project+'.pdf','application/pdf','create_packages',task.id,request)