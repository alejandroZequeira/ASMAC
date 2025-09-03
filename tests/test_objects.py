from asmac import ASMaC,Axo
from axo.contextmanager import AxoContextManager
from optikit.algorithms.moead import MOEAD
from optikit.problems import Problems
from optikit.algorithms.individual import Individual
import asyncio
import time as T
import pandas as pd
def create_object(alias):
        asm=ASMaC(host="148.247.202.72")
        problem = Problems()
        fn_problem = problem.evaluate_zdt1
        # Parámetros del problema
        n_var = 30
        bounds = [(0, 1)] * n_var
        n_runs = 2
        print(fn_problem)
        params = {
                "name": "nsga2",
                "label": "NSGA-II",
                "runs": 2, 
                "iters": 50,
                "m_objs": 2,
                "pop_size": 100,
                "params_mop": {"name": "dtlz1"},
                "params_crossover": {"name": "sbx", "prob": 1.0, "eta": 20},
                "params_mutation": {"name": "polymutation", "prob": 1./6, "eta": 15},
                "verbose": True,}
        moead: MOEAD = MOEAD(fn_problem, n_var, bounds, n_gen=200, n_sub=100, T=20)
        asm.user(user_name="alejandro",password="test_password")
        res=asyncio.run(asm.perstisify(obj=moead,alias=alias))
        return moead.__dict__
        
def test_create_individual(alias):
        asm=ASMaC(host="148.247.202.72")
        indi:Individual=Individual()
        asm.user(user_name="alejandro",password="test_password")
        res=asyncio.run(asm.perstisify(obj=indi,alias=alias))
        print(res)
        
        
def get_object(alias):
        asm=ASMaC(host="148.247.202.72")
        asm.user(user_name="alejandro",password="test_password")
        res=asyncio.run(asm.get_object_by_alias(alias=alias))
        print(res)
        return res

if __name__ == "__main__":
        asm=ASMaC(host="148.247.202.72")
        user_name = "alejandro"
        password = "test_password"
        name = "Test User"
        #result = asm.create_user(user_name=user_name, password=password, name=name)
        #print("result",result)
        # data=[]
        # for i in range(1,31):
        #         start=T.time()
        #         alias="individual"+str(i+31)
        #         test_create_individual(alias)
        #         data.append({"run":i,"alias_obj":alias,"response_time":T.time()-start})
        # df = pd.DataFrame(data)
        # df.to_csv("times_create_object_individuals.csv")
        # get_object("individual")
        # create_object()
        # data=[]
        # for i in range(1,31):
        #         start=T.time()
        #         alias="moea_"+str(i+51)
        #         d=create_object(alias)
        #         data.append({"run":i,"alias_obj":alias,"response_time":T.time()-start,"status":d})
        # df = pd.DataFrame(data)
        # df.to_csv("times_create_object_moea_2.csv")
        data=[]
        for i in range(1,31):
                start=T.time()
                alias="moea_"+str(i+51)
                d=get_object(alias)
                res=asm.run(d,"get_pareto_front")
                data.append({"run":i,"alias_obj":alias,"response_time":T.time()-start,"response":res})
        df = pd.DataFrame(data)
        df.to_csv("times_get_object_moea_3.csv")
        #print(res)
        
        asm.user(user_name="alejandro",password="test_password")
        asm.get_objects()