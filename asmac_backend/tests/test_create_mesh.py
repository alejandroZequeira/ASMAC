from asmac_backend.asmac_backend.v0 import ASMaC_Backend

def create_mesh():
    # Arrange
    user_name = "alejandro"
    password = "test_password"
    mesh_name = "Test Mesh"
    description = "This is a test mesh"

    # Act
    user = ASMaC_Backend.login_user(user_name=user_name, password=password)
    result = ASMaC_Backend.create_mesh(mesh_name=mesh_name, description=description, user_id=user["user_id"])
    print(result)
    
if __name__ == "__main__":
    create_mesh()