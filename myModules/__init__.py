'''
    The file name __init__ treats the directory as a package. When the directory is imported and the __init__.py exists, the code gets execute. In this case it imports specific code from simplemod1 by setting __all__ then imports two particular functions from the module.
'''
__all__ = ['logModule']
import logModule