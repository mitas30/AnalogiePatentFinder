from models.model import patentDocument

def m_test1():
    tester=patentDocument()
    list=tester.get_all_problems_dont_have_span_problem_list()
    for doc in list:
        print(doc)