## Privacy First RIUS Tracing to keep track of:
## - Embedding models used
## - LLMs called, token consumed, and response times

import os
import logging ## to log information about the observability of the events
from functools import wraps ## to create decorators for functions

log = logging.getLogger(__name__) ## create a logger for this module

def initialize():
    """ This is called once, before the main application modules.
        It will load the environment variables from .env and setup RIUS key and service name for observability.
    """
    from dotenv import load_dotenv ## load environment variables from .env file
    load_dotenv() ## load the environment variables from .env file

    ## check if RIUS_API_KEY is set and if the tracking is disabled via RIUS_DISABLED environment variable. If either condition is true, log that Rius observability is disabled and return.
    if not os.get_env("RIUS_API_KEY") or os.get_blocking("RIUS_DISABLED","false").lower() in ("1","true","yes"):
        log.info("Rius observability disabled or no key is provided")
        return ## this will exit the function and not initialize Rius observability

    # if everything is fine, we import rius and initialize it with the service name and capture content set to False. 
    # If any exception occurs during this process, we log the exception and continue without telemetry.
    try:
        import rius
        rius.init(service_name=os.getenv("RIUS_SERVICE_NAME","enterprise-qa-module"), capture_content=False) ## set the service name and do not capture content for privacy reasons
        log.info("Rius observability enabled") ## log that Rius observability is enabled
    except Exception:
        log.exception("Rius initialization has failed; application will continue without tracking") ## log the exception and continue without telemetry


def trace(name):
    """ This is a decorator function that can be used to trace sync/async functions.
        It will never export arguments or return values for privacy reasons.
        It is basically a wrapper around the rius.observe function that is used to trace the function calls.
        It will be used to trace the embedding and LLM functions in the application.
        It will be invoked as @trace("function_name") above the function definition.
        Everytime it is called, we will see what function is being called and how long it took to execute in the Rius dashboard.
        It will also see the latency of the function calls and the number of times it was called.
    """
    def decorate(fn):
        try:
            import rius
            return rius.observe(name=name,capture_input=False,capture_output=False)(fn)
            ## Here we are using the rius.observe function to trace the function calls.
            ## We are providing (fn) as the function that we want to trace and name of the function as the name parameter.
            ## We are also setting capture_input and capture_output to False to not capture the input and output of the function for privacy reasons.
        except ImportError:
            return fn 
            ## Here we are returning the original function, if rius module did not import the observability module. 
            ## This is to ensure that the application continues to work even if the rius module is not available.
        return decorate

    ## Here the operation is that we will just call the decorate function in other modules and pass the function name we want to tarce as params.
    ## Execution step: Fn runs first --> rius.observe is called --> function is traced
    
    ## Initialization function is called at once the application starts 
    ## and the trace function is called everytime a function is called that is decorated with @trace("function_name") 