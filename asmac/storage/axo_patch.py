"""
Parche para axo.storage.data._get_active_object
Evita el error NameError: name 'Axo' is not defined
"""

import types
import cloudpickle as cp
from option import Ok, Err

# Importamos la clase original de storage_service
import axo.storage.data as axo_data


async def _patched_get_active_object(self, *, key: str, bucket_id: str):
    code_res = await self.client.get(
        bucket_id=bucket_id,
        key=f"{key}_source_code",
        max_retries=100,
        delay=2,
        chunk_size="1MB"
    )
    attrs_res = await self.client.get(
        bucket_id=bucket_id,
        key=f"{key}_attrs",
        max_retries=100,
        delay=2,
        chunk_size="1MB"
    )
    if code_res.is_err:
        return Err(Exception("Failed to get source code"))
    if attrs_res.is_err:
        return Err(Exception("Failed to get attrs"))

    source_code_response = code_res.unwrap()
    source_code = cp.loads(source_code_response.data.tobytes())
    attrs_response = attrs_res.unwrap()
    attrs = cp.loads(attrs_response.data.tobytes())

    # 👇 import diferido para evitar el circular import
    from axo.core.axo import Axo, axo_method  

    mod = types.ModuleType("__axo_dynamic__")
    mod.__dict__["Axo"] = Axo
    mod.__dict__["axo_method"] = axo_method

    class_name = source_code_response.metadatas[0].tags.get("axo_class_name")
    exec(source_code, mod.__dict__)
    X = getattr(mod, class_name)

    print("ATTRS", attrs)
    obj = X(**attrs)
    for attr_name, attr_value in attrs.items():
        setattr(obj, attr_name, attr_value)
    return Ok(obj)


# 🚀 Aplicar monkey patch
axo_data.StorageService._get_active_object = _patched_get_active_object
print("[ASMAC PATCH] axo.storage.data._get_active_object ha sido parcheado correctamente")
