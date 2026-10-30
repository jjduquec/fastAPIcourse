from fastapi import FastAPI,Query,Body,HTTPException
from pydantic import BaseModel,Field,field_validator
from typing import Optional,List

app=FastAPI(title="First API") 

BLOG_APP=[
    {"id":1,"title":"mi primer post","content":"este es mi primer post"},
    {"id":2,"title":"mi segundo post","content":"este es mi segundo post"},
    {"id":3,"title":"mi tercer post","content":"este es mi tercer post"},
]

class PostBase(BaseModel):
    title:str  
    content:Optional[str]=None

class PostCreate(PostBase):
    title:str=Field(
        ..., #hace que el campo sea obligatorio
        min_length=10,
        max_length=100,
        examples=["el titulo debe contener entre 10 y 100 palabras"]
    )
    content:Optional[str]=Field(
        min_length=10,
        max_length=500,
        examples=["el contenido debe tener entre 10 y 500 palabras"] 
    )

    @field_validator("title")
    @classmethod 
    def not_allowed_titles_content(cls,value:str)->str:  
        if "spam" in value.lower(): 
            raise ValueError("El titulo no puede contener la palabra spam")
        return value 
        
class PostPublic(PostBase): 
    id:int  

class PostSummary(BaseModel):  
    id:int  
    title:str   

class PostUpdate(BaseModel):
    title:str  
    content:Optional[str]=None  


@app.get("/")
def home():
    return {'message':'Hello World from FastAPI'} 

@app.get("/posts",response_model=List[PostPublic])
def list_posts(query:str|None=Query(default=None,description="Parametro para buscar blogs")):  
    if query:  
        results=[post for post in BLOG_APP if query.lower() in post['title'].lower()]
        return results
    else:
        return BLOG_APP

@app.get("/post/{id}")
def get_post(id:int,get_content:bool=Query(default=False,description="Parametro para recuperar o no el contenido de un post")):
    for post in BLOG_APP:  
        if post["id"]==id:  
            if not get_content: 
                data={"id":post["id"],"title":post["title"]} 
            else: 
                data=post  
            return {"data":data} 
    return {"data":"Post no encontrado"}

@app.post("/post")
def create_post(post:PostCreate): 
    
    
    new_id=len(BLOG_APP)+1 
    new_post={"id":new_id,"title":post.title,"content":post.content}
    BLOG_APP.append(new_post) 
    respuesta={"message":"el post se ha creado exitosamente","id":new_id}

    return respuesta
    

@app.put("/post/{post_id}")
def update_post(post_id:int,data:PostUpdate): 
    for post in BLOG_APP:  
        if post["id"]==post_id: 
            payload=data.model_dump(exclude_unset=True)
            if "title" in payload: post["title"]=payload["title"]
            if "content" in payload: post["content"]=payload["content"]
            return {"message":"post actualizado exitosamente","post":post} 
    raise HTTPException(status_code=404,detail="post not found")


@app.delete("/post/{post_id}",status_code=204) 
def delete_post(post_id:int):  
    for index,post in enumerate(BLOG_APP):  
        if post["id"]==post_id:
            BLOG_APP.pop(index)
            return 
    raise HTTPException(status_code=404,detail="post not found")
