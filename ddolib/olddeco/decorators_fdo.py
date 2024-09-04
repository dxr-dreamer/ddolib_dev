def FDO(input_ddos=[], output_ddos=[], relationship_text="", register=0):
    """
    Decorator to define a Function Digital Object (FDO).

    Parameters:
    input_ddos (list): List of the names of all input ddos as parameters.
    output_ddos (list): List of the names of all output ddos as parameters.
    relationship_text (str): Description of the relationship.
    register (int): Registration flag.

    Returns:
    function: The wrapped function that handles input and output DDOs and manages relationships.
    """
    def decorator(func,iid=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 提取 DataDigitalObject 实例并剥离 data 属性
            new_args = []
            input_objects = []
            for arg in args:
                logger.debug(f"Processing argument: {arg}")
                if isinstance(arg, DataDigitalObject):
                    logger.debug(f"Argument {arg} is a DataDigitalObject, extracting data")
                    new_args.append(arg.data)
                    input_objects.append(arg)
                else:
                    new_args.append(arg)

            logger.debug(f"New arguments for function call: {new_args}")

            # 执行原始函数
            result = func(*new_args, **kwargs)
            logger.debug(f"Output data from function call: {result}")
            
            fdo_metadata = {
                "function": func.__name__,
                "input_ddos": input_ddos,
                "output_ddos": output_ddos,
                "relationship_text": relationship_text,
                "register": register
            }
            '''
            if iid == None:
                fdo = FunctionDigitalObject(decorator(func,), fdo_metadata)
                fdo_iid = fdo.iid
            else:
                fdo_iid = iid
            '''
            fdo = FunctionDigitalObject(func, fdo_metadata)
            fdo_iid = fdo.iid
            logger.debug(f"Created new FDO with iid: {fdo_iid}")

            # 处理输出的 DDO
            if not isinstance(result, tuple):
                result = (result,)

            output_objects = []
            for res in result:
                if isinstance(res, DataDigitalObject):
                    output_objects.append(res)

            # 创建关系
            from_ddo_iids = [input_ddo.iid for input_ddo in input_objects]
            to_ddo_iids = [output_ddo.iid for output_ddo in output_objects]
            rel_metadata = {
                "type": "Func",
                "func": fdo_iid,
                "description": relationship_text
            }
            relationship = Relationship(from_ddo_iids=from_ddo_iids, to_ddo_iids=to_ddo_iids, metadata=rel_metadata)
            logger.debug(relationship)

            if register:
                # 这里可以添加 FDO 注册逻辑
                pass

            if len(result) == 1:
                return result[0]
            return result
        
        return wrapper
    
    return decorator