create table usuario (

    id INT NOT NULL auto_increment,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    idade INT,
    tipo_sanguineo VARCHAR(5),
    sexo VARCHAR(15),
    primary key (id)
    
)default charset = utf8;

create table contato (

	id INT NOT NULL auto_increment,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    mensagem VARCHAR(1500),
    telefone VARCHAR(20),
    primary key (id)
    
)default charset = utf8;

select * from contato;

select * from usuario;