from fastapi import FastAPI,Query,Body,HTTPException,Path
from pydantic import BaseModel,Field,field_validator,EmailStr
from typing import Optional,List,Union,Literal

app=FastAPI(title="First API") 

BLOG_APP=[
    {"id":1,"title":"mi primer post","content":"este es mi primer post"},
    {"id":2,"title":"mi segundo post","content":"este es mi segundo post"},
    {"id":3,"title":"mi tercer post","content":"este es mi tercer post"},
]

class Tag(BaseModel):
    name:str=Field(
        ...,
        min_length=4,
        max_length=20
    )

class Author(BaseModel): 
    name:str 
    email:EmailStr

class PostBase(BaseModel):
    title:str  
    content:str 
    tags:Optional[List[Tag]]=Field(default_factory=list)
    author:Optional[Author]=None

class PostCreate(PostBase):
    title:str=Field(
        ..., #hace que el campo sea obligatorio
        min_length=4,
        max_length=100,
        examples=["el titulo debe contener entre 10 y 100 palabras"]
    )
    content:Optional[str]=Field(
        min_length=4,
        max_length=500,
        examples=["el contenido debe tener entre 10 y 500 palabras"] 
    )

    tags:List[Tag]=[]
    author:Optional[Author]=None
 
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
    title:Optional[str]=Field(
        None,
        min_length=3,  
        max_length=500
    ) 
    content:Optional[str]=None  


@app.get("/")
def home():
    return {'message':'Hello World from FastAPI'} 

@app.get("/posts",response_model=List[PostPublic])
def list_posts(query:Optional[str]|None=Query(
    default=None,
    description="Parametro para buscar blogs",
    alias="search",
    min_length=2,
    max_length=100
    ),
    limit:int= Query(
        10, 
        ge=1,  
        le=50,
        description="Numero de resultados entre 1 y 50"
    ),

    offset:int=Query(
        0,
        ge=0, 
        description="elementos a saltar en la lista" 

    ), 
    order_by:Literal["id","title"]=Query(
        "id",
        description="Campo de orden para el ordenamiento"
    ), 
    direction:Literal["asc","desc"]=Query(
        "asc", 
        description="Ordenamiento ascendente (asc) o descendente (desc) "
    )
    
    
    ):  

    results=BLOG_APP
    if query:  
        results=[post for post in BLOG_APP if query.lower() in post['title'].lower()]
        results=sorted(results,key=lambda post:post[order_by],reverse=(direction=="desc"))

    return results[offset:offset+limit]  

@app.get("/post/{id}",response_model=Union[PostSummary,PostPublic],response_description="Post encontrado")
def get_post(id:int=Path(
    ...,
    ge=1,  
    description="El id debe ser mayor o igual a 1",
    example=1 
    ),
    get_content:bool=Query(default=False,description="Parametro para recuperar o no el contenido de un post")):
    for post in BLOG_APP:  
        if post["id"]==id:  
            if not get_content: 
                return {"id":post["id"],"title":post["title"]} 
            else: 
                return post  
            
    raise HTTPException(status_code=404,detail="Post no encontrado")

@app.post("/post",response_model=PostSummary,response_description="El post se ha creado exitosamente")
def create_post(post:PostCreate): 
    
    new_id=len(BLOG_APP)+1 
    new_post={"id":new_id,
              "title":post.title,
              "content":post.content,
              "tags":[tag.model_dump() for tag in post.tags],
              "author": post.author.model_dump() if post.author else None
              }
    BLOG_APP.append(new_post) 
    

    return new_post
    

@app.put("/post/{post_id}",response_model=PostUpdate,response_description="El post ha sido actualizado")
def update_post(post_id:int,data:PostUpdate): 
    for post in BLOG_APP:  
        if post["id"]==post_id: 
            payload=data.model_dump(exclude_unset=True)
            if "title" in payload: post["title"]=payload["title"]
            if "content" in payload: post["content"]=payload["content"]
            if "author" in payload: post["author"]=payload["author"].model_dump()
            return post
    raise HTTPException(status_code=404,detail="post not found")


@app.delete("/post/{post_id}",status_code=204) 
def delete_post(post_id:int):  
    for index,post in enumerate(BLOG_APP):  
        if post["id"]==post_id:
            BLOG_APP.pop(index)
            return {"message":"El post se ha eliminado"}
    raise HTTPException(status_code=404,detail="post not found")
