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
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

# ===============================================================
# Funções
# ===============================================================

def avg_std_time_on_traffic( df1 ):
    """ Esta função calcula o tempo médio e o desvio padrão do tempo por cidade e densidade de trânsito.
        Input: Dataframe
        Output: Gráfico de sunburst com o tempo médio e o desvio padrão da Cidade e densidade de trânsito.

    """

    df1_aux = ( df1.loc[:,['Time_taken(min)', 'City', 'Road_traffic_density']]
                    .groupby(['City','Road_traffic_density'])
                    .agg(['mean', 'std']).reset_index() )
                    
    df1_aux.columns = ['City', 'Road_traffic_density', 'mean_time_by_city_density', 'std_time_by_city_density']

    fig= px.sunburst( df1_aux, path=['City', 'Road_traffic_density'], values='mean_time_by_city_density',
                                    color='std_time_by_city_density',color_continuous_scale='RdBu',
                                    color_continuous_midpoint=np.average(df1_aux['std_time_by_city_density']))
    return fig
            
# ================================================================================

def avg_std_time_graph( df1 ):
    """ Esta função calcula o tempo médio e o desvio padrão do tempo por cidade.
        Input: Dataframe
        Output: Gráfico de barras com o tempo médio e o desvio padrão.

    """

    df1_aux = df1.loc[:,['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std']).reset_index()
    df1_aux.columns = ['City', 'mean_time_by_City', 'std_time_by_city']
                        
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',x=df1_aux['City'], y=df1_aux['mean_time_by_City'],
                                            error_y=dict(type='data', array=df1_aux['std_time_by_city'] ) ) )
    fig.update_layout(barmode='group')

    return fig

# ================================================================================

def avg_std_time_festival(df1, festival,  op):
    """ Esta função calcula o tempo médio e o desvio padrão do tempo de entrega no Festival.
            Parâmetros:
                input:
                    - df1: Dataframe com os dados necessários para o calculo.
                    
                    - op: Tipo de Operação que precisa ser calculado.
                        'avg_time': Calcula o tempo médio.
                        'std_time': Calcula o desvio padrão do tempo.
                    
                    - festival: Tipo de operação que diz se é ou não festival.
                        Yes: Sim
                        No: Não
    """
    df1_aux = ( df1.loc[:,['Time_taken(min)', 'Festival']]
                    .groupby('Festival')
                    .agg(['mean', 'std']) )
           
    df1_aux.columns = ['avg_time' , 'std_time']
    df1_aux = df1_aux.reset_index()
    df1_aux = df1_aux.loc[df1_aux['Festival'] == 'Yes', op ].round(2)

    return df1_aux

# ================================================================================

def distance_mean(df1, fig):
    """ 1 part:
            Esta função calcula a média de distância dos restaurantes e locais de entregas.
            Input: Dataframe
            Output: Valor com a média de distância
        
        2 part:
            Esta função calcula a porcentagem média de distância dos restaurantes e locais de entregas por cidade
            Input: Dataframe
            Output: gráfico de pizza com a média da coluna distacia por cidade.


    """
    if fig == False:
            
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
                    
        df1['distance'] = ( df1.loc[:, cols]
                                .apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )

        avg_distance = df1['distance'].mean().round(2)

        return avg_distance
    
    else:
        
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude' ]
        df1['distance'] = ( df1.loc[:, cols].apply( lambda x: 
                                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )

        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            
        return fig


# ================================================================================

def clean_code(df1):
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

# ==========================================================================================
# Importando o dataset
df = pd.read_csv('../dataset/train.csv')

#Cleaning dataset
df1 = clean_code( df )

#==================================================================
# Barra Lateral
#==================================================================

st.header('Marketplace - Visão Restaurantes')

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
        
        st.title( "Overall Metrics ")

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            
            deliver_unique = df1['Delivery_person_ID'].nunique()
            col1.metric( 'Single Couriers', deliver_unique )
        
        with col2:
            avg_distance = distance_mean(df1, fig=False)
            col2.metric('A distância média', avg_distance )

        with col3:
            df1_aux = avg_std_time_festival(df1, 'Yes', 'avg_time')
            col3.metric( 'Tempo médio c/ Festival', df1_aux )

        with col4:
            df1_aux = avg_std_time_festival(df1, 'Yes', 'std_time')
            col4.metric( 'STD entrega c/ Festival', df1_aux )
        
        with col5:
            df1_aux = avg_std_time_festival(df1, 'No', 'avg_time')
            col5.metric( 'Tempo médio s/ Festival', df1_aux )
        
        with col6:
            df1_aux = avg_std_time_festival(df1, 'No', 'std_time')
            col6.metric( 'STD Entrega s/ Festival', df1_aux )
        
        st.markdown("""___""")
    with st.container():
        
        st.markdown( "###### Distribuição do tempo por cidade ")

        col1, col2 = st.columns([4, 3], gap='small')
        
        with col1:
            fig = avg_std_time_graph( df1)
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            st.markdown( "###### Média e desvio padrão do tempo por cidade e tipo de pedido ")
            
            df1_aux =( df1.loc[:,['Time_taken(min)', 'City', 'Type_of_order']]
                    .groupby(['City','Type_of_order']).agg(['mean', 'std']).reset_index() )
            
            df1_aux.columns = ['City', 'Type_of_order', 'mean_time_by_city_order', 'std_time_by_city_order']

            st.dataframe(df1_aux)

       
    
    with st.container():
        st.markdown("""___""")
        st.markdown( "#### Distribução do Tempo por cidade e tipo de tráfego ")
        
        
        col1, col2 = st.columns([3, 4], gap='small')
        
        with col1:
            
            fig = distance_mean(df1, fig=True)
            st.plotly_chart(fig , use_container_width=True)

            
            
        
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart(fig , use_container_width=True)
            
            




        
        
   


        
