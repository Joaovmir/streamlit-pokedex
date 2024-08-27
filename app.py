import requests
import streamlit as st
import pickle

def get_pokemon_by_name(name):
    return requests.get(f'https://pokeapi.co/api/v2/pokemon/{name}')

def extrai_tipos(tipos):
    tipo1 = tipos[0]['type']['name']
    try:
        tipo2 = tipos[1]['type']['name']
    except IndexError:
        tipo2 = None
    return [tipo1, tipo2]

def extrai_imagem(response):
    imagem = response.json()['sprites']['front_default']
    return imagem

def extrai_evolucao(evolucoes):
    url_evolution = requests.get(evolucoes).json()['evolution_chain']['url']
    infos_evolucoes_pokemon = requests.get(url_evolution).json()
    primeiro_pokemon = infos_evolucoes_pokemon['chain']['species']['name']
    imagem_primeiro_pokemon = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{infos_evolucoes_pokemon["chain"]["species"]["url"].split("/")[-2]}.png'
    try:
        quantidade_evolucoes = len(infos_evolucoes_pokemon['chain']['evolves_to'])
        if quantidade_evolucoes>1:
            segundo_pokemon = []
            imagem_segundo_pokemon = []
            for i in range(quantidade_evolucoes):
                segundo_pokemon.append(infos_evolucoes_pokemon['chain']['evolves_to'][i]['species']['name'])
                imagem_segundo_pokemon.append(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{infos_evolucoes_pokemon["chain"]["evolves_to"][i]["species"]["url"].split("/")[-2]}.png')
        else:
            segundo_pokemon = infos_evolucoes_pokemon['chain']['evolves_to'][0]['species']['name']
            imagem_segundo_pokemon = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{infos_evolucoes_pokemon["chain"]["evolves_to"][0]["species"]["url"].split("/")[-2]}.png'
    except:
        segundo_pokemon = None
        imagem_segundo_pokemon = None
    try:
        terceiro_pokemon = infos_evolucoes_pokemon['chain']['evolves_to'][0]['evolves_to'][0]['species']['name']
        imagem_terceiro_pokemon = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{infos_evolucoes_pokemon["chain"]["evolves_to"][0]["evolves_to"][0]["species"]["url"].split("/")[-2]}.png'
    except:
        terceiro_pokemon = None
        imagem_terceiro_pokemon= None
    return [primeiro_pokemon, segundo_pokemon, terceiro_pokemon, imagem_primeiro_pokemon, imagem_segundo_pokemon, imagem_terceiro_pokemon]

def pokemon_from_api(response):
    infos = response.json()
    id = infos['id']
    altura = infos['height'] 
    peso = infos['weight']
    tipos = infos['types']
    nome = infos['name']
    imagem = infos['sprites']['front_default']
    habilidade = [infos['abilities'][0]['ability']['name'], 
                  infos['abilities'][0]['ability']['url']]
    movimentos = [(move['move']['name'], move['move']['url']) for move in infos['moves']]
    evolucoes = infos['species']['url']
    return {
        'id':id,
        'nome':nome,
        'tipo1':extrai_tipos(tipos)[0],
        'tipo2':extrai_tipos(tipos)[1],
        'peso': float(peso),
        'altura': float(altura),
        'habilidade': habilidade,
        'movimentos': movimentos,
        'evolucao1': extrai_evolucao(evolucoes)[0],
        'evolucao2': extrai_evolucao(evolucoes)[1],
        'evolucao3': extrai_evolucao(evolucoes)[2],
        'img_evolucao1': extrai_evolucao(evolucoes)[3],
        'img_evolucao2': extrai_evolucao(evolucoes)[4],
        'img_evolucao3': extrai_evolucao(evolucoes)[5],
        'imagem': imagem
    }

def pokedex(offset):
    infos = requests.get(f'https://pokeapi.co/api/v2/pokemon/?offset={(offset-1)*20}&limit=20').json()
    nomes = []
    ids = []
    imagens = []
    for pokemon in infos['results']:
        nomes.append(pokemon['name'])
        id = pokemon['url'].split('/')[-2]
        ids.append(id)
        imagens.append(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png')
    
    return {
        'nomes': nomes,
        'ids': ids,
        'imagens': imagens
    }

menu = st.sidebar.selectbox('Menu:', ('Pokédex', 'Pesquisa Pokémon', 'Previsão de lendários'))

with st.container():
    _,center,_ = st.columns(3)
    with center:
        st.image('https://logosmarcas.net/wp-content/uploads/2020/05/Pokemon-Logo.png', width = 256)

if menu == 'Pesquisa Pokémon':
        
    nome_pokemon = st.text_input('Digite o nome ou ID do Pokemon:').lower()

    try:
        if(nome_pokemon):
            response = get_pokemon_by_name(nome_pokemon)
            infos_pokemon = pokemon_from_api(response)
            habilidade_pokemon = requests.get(infos_pokemon['habilidade'][1]).json()
            for descricao in habilidade_pokemon['effect_entries']:
                if descricao['language']['name'] == 'en':
                    descricao_habilidade = descricao['short_effect']
            st.title(f'{infos_pokemon["nome"].title()} - Nº {infos_pokemon["id"]}')
            with st.container():
                coluna1, coluna2 = st.columns(2)
                with coluna1:
                    st.image(infos_pokemon['imagem'], width=128)
                    st.markdown('#### Tipos')
                    st.markdown(infos_pokemon['tipo1'].title())
                    if infos_pokemon['tipo2']:
                        st.markdown(infos_pokemon['tipo2'].title())
                with coluna2:
                    st.markdown('#### Altura')
                    st.markdown(infos_pokemon["altura"])
                    st.markdown('#### Peso')
                    st.markdown(infos_pokemon["peso"])
                    st.markdown('#### Habilidade')
                    with st.expander(infos_pokemon["habilidade"][0].title()):
                        st.markdown(descricao_habilidade)
            with st.container():
                st.markdown('### Evoluções')
                if not isinstance(infos_pokemon['evolucao2'], list):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image(infos_pokemon['img_evolucao1'], width=128, caption = infos_pokemon['evolucao1'].title())
                    if infos_pokemon['evolucao2']:
                        with col2:
                            st.image(infos_pokemon['img_evolucao2'], width=128, caption = infos_pokemon['evolucao2'].title())
                    if infos_pokemon['evolucao3']:
                        with col3:
                            st.image(infos_pokemon['img_evolucao3'], width=128, caption = infos_pokemon['evolucao3'].title())
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image(infos_pokemon['img_evolucao1'], width=128, caption = infos_pokemon['evolucao1'].title())
                    with col2:
                        for i in range(0,len(infos_pokemon['evolucao2']),2):
                            st.image(infos_pokemon['img_evolucao2'][i], width=128, caption = infos_pokemon['evolucao2'][i].title())
                    with col3:
                        for i in range(1,len(infos_pokemon['evolucao2']),2):
                            st.image(infos_pokemon['img_evolucao2'][i], width=128, caption = infos_pokemon['evolucao2'][i].title())
            
            with st.container():
                botao_moves = st.button('Ver Moves')
                if botao_moves:
                    st.markdown('### Moves')
                    for movimento in infos_pokemon['movimentos']:
                        info_movimento = requests.get(movimento[1]).json()['effect_entries']
                        for descricao in info_movimento:
                            if descricao['language']['name'] == 'en':
                                descricao_move = descricao['short_effect']
                        with st.expander(movimento[0].title()):
                            st.markdown(descricao_move)
                        
    except:
        st.write("Pokémon Inválido")

if menu == 'Pokédex':
    pagina = st.number_input('Selecione uma página (1-57)', 1, 57, 1, format='%d')

    infos_pokemons = pokedex(pagina)
    coluna_pokedex1, coluna_pokedex2, coluna_pokedex3, coluna_pokedex4 = st.columns(4)
    with coluna_pokedex1:
        for i in range(0, len(infos_pokemons['nomes']), 4):
            st.image(infos_pokemons['imagens'][i], width=128, caption = f'{infos_pokemons["nomes"][i].title()} - Nº {infos_pokemons["ids"][i]}')
    with coluna_pokedex2:
        for i in range(1, len(infos_pokemons['nomes']), 4):
            st.image(infos_pokemons['imagens'][i], width=128, caption = f'{infos_pokemons["nomes"][i].title()} - Nº {infos_pokemons["ids"][i]}')
    with coluna_pokedex3:
        for i in range(2, len(infos_pokemons['nomes']), 4):
            st.image(infos_pokemons['imagens'][i], width=128, caption = f'{infos_pokemons["nomes"][i].title()} - Nº {infos_pokemons["ids"][i]}')
    with coluna_pokedex4:
        for i in range(3, len(infos_pokemons['nomes']), 4):
            st.image(infos_pokemons['imagens'][i], width=128, caption = f'{infos_pokemons["nomes"][i].title()} - Nº {infos_pokemons["ids"][i]}')

if menu == 'Previsão de lendários':
    modelo = pickle.load(open('models/modelo_pokemon.sav', 'rb'))
    st.markdown('### Previsão de Lendários')
    with st.form('Formulário', clear_on_submit=True):
        st.markdown('### Status')
        coluna_a, coluna_b, coluna_c = st.columns(3)

        with coluna_a:
            hp = st.number_input('HP', min_value=0)
            attack = st.number_input('Ataque', min_value=0)
        with coluna_b:
            defense = st.number_input('Defesa', min_value=0)
            spattack = st.number_input('Ataque Especial', min_value=0)
        with coluna_c:
            spdefense = st.number_input('Defesa Especial', min_value=0)
            speed = st.number_input('Velocidade', min_value=0)
        
        st.markdown("### Tipos")
        coluna_d, coluna_e, coluna_f, coluna_g, coluna_h, coluna_i = st.columns(6) 

        with coluna_d:
            grass = st.checkbox('Grass')
            fire = st.checkbox('Fire')
            water = st.checkbox('Water')
        with coluna_e:
            bug = st.checkbox('Bug')
            normal = st.checkbox('Normal')
            poison = st.checkbox('Poison')
        with coluna_f:
            electric = st.checkbox('Eletric')
            ground = st.checkbox('Ground')
            fairy = st.checkbox('Fairy')
        with coluna_g:
            fighting = st.checkbox('Fighting')
            psychic = st.checkbox('Psychic')
            rock = st.checkbox('Rock')
        with coluna_h:
            ghost = st.checkbox('Ghost')
            ice = st.checkbox('Ice')
            dragon = st.checkbox('Dragon')
        with coluna_i:
            dark = st.checkbox('Dark')
            steel = st.checkbox('Steel')
            flying = st.checkbox('Flying')
        
        is_evolution = st.checkbox('É uma evolução de outro Pokémon?')
        submitted = st.form_submit_button('Confirmar')
        if submitted:
            previsao = modelo.predict([[hp, attack, defense, spattack, spdefense, speed,
                is_evolution, bug, dark, dragon, electric, fairy,
                fighting, fire, flying, ghost, grass, ground, ice,
                normal, poison, psychic, rock, steel, water]])
            
            if previsao == [0]:
                st.markdown('#### Pokémon Comum')
            if previsao == [1]:
                st.markdown('#### Pokémon Lendário!')
    
