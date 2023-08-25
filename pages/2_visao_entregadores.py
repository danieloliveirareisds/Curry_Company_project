# Libraries
from haversine import haversine 
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# bibliotecas necessarias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')

# ===============================================================
# Funções
# ===============================================================

def top_delivers(df1, top_asc):
    """ Esta função tem a responsabilidade de mostrar as tabelas onde tem os top 10 entregadores
    mais rápidos e os mais lentos por cidades.

    1. Ela calcula a media de tempo de todas as entregas feitas de cada entregador por cidade.
    
    Input: Dataframe
    Output: Dataframe com a média de tempo de entrega dos entregadores por cidades.
        
    """
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City'] ]
                .groupby( ['City', 'Delivery_person_ID'] )
                .mean()
                .sort_values(['Delivery_person_ID', 'Time_taken(min)'], ascending=top_asc)
                .reset_index()
                .round(2) )
    # Selecionando somente as 10 primeiras linhas de cada cidade.
    df_aux1 = df2.loc[df2[ 'City' ] == 'Metropolitian', : ].head( 10 )
    df_aux2 = df2.loc[df2['City' ] == 'Urban', : ].head( 10 )
    df_aux3 = df2.loc[df2[ 'City' ] == 'Semi-Urban', : ].head( 10 )
                
    # Concatenação de variáveis recebendo somente as cidades e as 10 primeiras linhas.
    df_avg_time_max_per_deliver = ( pd.concat( [df_aux1, df_aux2, df_aux3] )
                                           .reset_index( drop=True ) )

    return df_avg_time_max_per_deliver


def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe
    """

    # 1. convertendo a coluna Age de texto para número
    #float = decimal
    #int = inteiro
    #str = objetct
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN ' # O simbolo != utiliza quando queremos dados diferentes do modelo que queremos
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int64')


    # 2. convertendo a coluna Ratings de texto para numero decimal (Float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )


    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )


    # 4. convertendo a coluna multiple_deliveries de texto para numero inteiro
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int64')

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Weatherconditions'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()


    # 5 retirando os espaços dentros das strings
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip() 
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 6 Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1]) 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype('int64')

    return df1

# import dataset
df = pd.read_csv('../dataset/train.csv')

# Cleaning Dataset
df1 = clean_code( df )

#==================================================================
# Barra Lateral
#==================================================================

st.header('Marketplace - Visão Entregadores')

# image_path = 'C:/Users\Daniel Reis/repos/ftc_programacao_python/1701680.png'
image = Image.open( '1701680.png')

st.sidebar.image( image, width=120)

st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 'Até qual valor?', 
                  value=datetime(2022, 4, 13), 
                  min_value=datetime(2022, 2, 11 ),
                  max_value=datetime(2022, 4, 6),
                  format='DD-MM-YYYY' )

st.header( date_slider )
st.sidebar.markdown( """___""" )

# Criando o filtro por densidade de tráfego
traffic_options = st.sidebar.multiselect( 
    'Quais as condições de trânsito?', 
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )
st.sidebar.markdown( """___""" )

conditions_options = st.sidebar.multiselect( 
    'Quais as condições climáticas?', 
    [ 'conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy',
     'conditions Sunny', 'conditions Windy' ],
    default=[ 'conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 
             'conditions Stormy', 'conditions Sunny', 'conditions Windy' ] )
st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powered by Daniel Reis' )

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtor de condições climáticas
linhas_selecionadas = df1['Weatherconditions'].isin(conditions_options)
df1 = df1.loc[linhas_selecionadas, :]



#==================================================================
# Layout no Streamlit
#==================================================================

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '' , ''] )

with tab1:
    
    with st.container():
        st.title( 'Overall Metrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        
        # =================== IDADES ============================
       
        with col1:
            # A menor idade dos Entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade )
            
        with col2:
            # A maior idade dos Entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade )
        
        # ================== CONDIÇÕES VEÍCULOS ============================
        
        with col3:
            # A melhor condição de veiculos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao )
          
        with col4:
            # A pior condição de veiculos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao )
        
        # ================ Avaliações por Entregador ============================
   
    with st.container():
        st.markdown("""___""")
        st.title( 'Avaliações ' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por Entregador' )
            df_avg_ratings_per_deliver =( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                         .groupby('Delivery_person_ID')
                                         .mean()
                                         .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )

        # ================ Avaliações por Trânsito ============================
        
        with col2:
            st.markdown( '##### Avaliação média por Trânsito' )
            df_avg_ratings_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                             .groupby('Road_traffic_density')
                                             .agg(['mean', 'std']) )
            # Mudança de nome das colunas
            df_avg_ratings_by_traffic.columns = ['Delivery_mean', 'Delivery_std'] 
            
            # Reset de Index
            df_avg_ratinsg_by_traffic = df_avg_ratings_by_traffic.reset_index()

            st.dataframe( df_avg_ratings_by_traffic )

        # ================ Avaliações por Condições Climáticas ============================
            
            st.markdown( '##### Avaliação média por clima' )
            df_avg_ratings_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                             .groupby( 'Weatherconditions' )
                                             .agg( [ 'mean', 'std' ]  ) )

            # Mudança de nome das colunas
            df_avg_ratings_by_weather.columns = ['Delivery_mean', 'Delivery_std']

            # Reset do Index
            df_avg_ratings_by_weather = df_avg_ratings_by_weather.reset_index()

            st.dataframe( df_avg_ratings_by_weather )

# ================ CONTAINERS DE VELOCIDADE DE ENTREGA ============================
    
    with st.container():
        st.markdown( """___""" )
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '##### Top Entregadores mais rápidos')
            df_avg_time_max_per_deliver = top_delivers( df1, top_asc=True  ) 
            st.dataframe( df_avg_time_max_per_deliver )
        
        
        with col2:
            st.markdown( '##### Top Entregadores mais lentos')
            df_avg_time_max_per_deliver = top_delivers( df1, top_asc=False  ) 
            st.dataframe( df_avg_time_max_per_deliver )     
