# Flash Cards - Projeto Integrador UNIVESP! :rocket:
* Essa é uma aplicação web utilizando flask com o uso de banco de dados e controle de versão para o ensino de idiomas por meio de flash cards 
* Feita para o uso educacional :pencil2:

## O que o programa faz:
* Criação do administrador (professor)
* Criação de alunos
* Possibilidade de criar cartas e inseri-las nos livros
* Possibilidade do professor gerenciar os alunos
* Alunos podem dizer se sabem ou não sabem o que a carta significa
* Alunos podem resetar as cartas de um livro para vê-las novamente

## Como usar:
* `git clone https://github.com/natanlimeira/UNIVESP2.git`
* `cd UNIVESP2`
* `pip install -r requirements.txt`
* `flask db init`
* `flask db migrate -m "users table"`
* `flask db migrate -m "cards table"`
* `flask db upgrade`
* `flask run`

## Caso apenas o flask não funcione:
* `python -m flask db init`
* Continuar com os outros passos


## Add-ons futuros:
* API para novas palavras
* Alunos poderem mudar de livro
* Professor adicionar grupos de palavras

## Como contribuir:
1. Fork desse repositório! `git clone https://github.com/natanlimeira/UNIVESP2.git`
2. Criar um feature branch: `git checkout -b my-new-feature`
3. Realizar Commit das mudanças: `git commit -m 'Add some feature'`
4. Realizar push no branch: `git push origin my-new-feature`
5. Submeter o pull request :+1:
