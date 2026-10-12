import platform
import pandas

print("pandas_version=%s" % pandas.__version__)
print("pandas_file=%s" % pandas.__file__)
print("python=%s" % platform.python_version())
print("implementation=%s" % platform.python_implementation())
print("platform=%s" % platform.platform())
