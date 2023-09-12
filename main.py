import pandas as pd
import streamlit as st
import plotly.express as px
from pypinyin import pinyin, Style


st.set_page_config(layout="wide")

# 侧边栏
with st.sidebar:
  st.title('SOH分析结果')  
  file = st.file_uploader(label="请上传*:red[SOH分析数据]*", accept_multiple_files=True)
  if len(file)>0:
    data = pd.read_excel(file[0], sheet_name=None)
    for i in ['全辆车SOH分布', '使用年限', '行驶里程', '活跃车辆-by品牌厂商等', '僵尸车辆-by品牌厂商等']:
      if i not in list(data):
        st.warning(f'请确认该数据表中含"{i}"表单', icon="⚠️")
        break

@st.cache_data
def read_data(filepath):
  summary = pd.read_excel(filepath, sheet_name='全辆车SOH分布', index_col=0)
  summary = summary.stack().reset_index().rename({'level_1':'SOH', 0:'车辆数量', '行标签':'车辆状态'}, axis=1)

  usage = pd.read_excel(filepath, sheet_name='使用年限', usecols=list(range(8)), index_col=[0,1,2], header=[1])
  usage.index.names = ['车辆活跃度', '使用年份', '驱动方式']
  usage = usage.stack().reset_index().rename({'level_3': 'SOH', 0:'车辆数量'}, axis=1)

  mileage = pd.read_excel(filepath, sheet_name='行驶里程', usecols=list(range(8)), index_col=[0,1,2], header=[1])
  mileage.index.names = ['车辆活跃度', '里程区间', '驱动方式']
  mileage = mileage.stack().reset_index().rename({'level_3': 'SOH', 0:'车辆数量'}, axis=1)

  active = pd.read_excel(filepath, sheet_name='活跃车辆-by品牌厂商等', usecols=list(range(12)), index_col=[0,1,2,3,4,5,6], header=[1])
  active.index.names = ['车辆公告号','车辆厂商','电池厂商','车辆类别','车辆用途','车型','驱动方式']
  active = active.stack().reset_index().rename({'level_7': 'SOH', 0:'车辆数量'}, axis=1)

  inactive = pd.read_excel(filepath, sheet_name='僵尸车辆-by品牌厂商等', usecols=list(range(12)), index_col=[0,1,2,3,4,5,6], header=[1])
  inactive.index.names = ['车辆公告号','车辆厂商','电池厂商','车辆类别','车辆用途','车型','驱动方式']
  inactive = inactive.stack().reset_index().rename({'level_7': 'SOH', 0:'车辆数量'}, axis=1)

  return [summary, usage, mileage, active, inactive]
# 主界面

[summary, usage, mileage, active, inactive] = read_data('./数据--输出.xlsx')

barSummary = px.bar(summary, x='SOH', y='车辆数量', color='车辆状态', title='全辆车SOH数量分布')
barSummary.update_layout(legend=dict(
    yanchor="top",
    y=-0.2,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
))
st.plotly_chart(barSummary, theme='streamlit', use_container_width=True)


tab1, tab2, tab3, tab4= st.tabs(["🕒年份", "🌏里程", "🚗活跃车辆", "🛑僵尸车辆"])

with tab1:
  acOrNot = list((usage['车辆活跃度'].unique()))
  drive = list(usage['驱动方式'].unique())
  col1, col2= st.columns(2, gap='large')
  x = col1.multiselect('选择车辆活跃度类型', acOrNot)
  y = col2.multiselect('驱动方式', drive)

  # if st.button('确定'):
  select = usage
  if len(x)>0:
    select = usage[(usage['车辆活跃度'].isin(x))]
  if len(y)>0:
    select = usage[(usage['驱动方式'].isin(y))]

  fig_hist = px.histogram(select, x='使用年份', y='车辆数量', color='SOH')
  fig_hist.update_layout(legend=dict(
    yanchor="top",
    y=-0.2,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))
  fig_hist.update_layout(yaxis_title='车辆数量')
  st.plotly_chart(fig_hist, theme='streamlit', use_container_width=True, height=200)

  fig_box = px.box(select, x='使用年份', y='车辆数量', color='SOH')
  fig_box.update_layout(legend=dict(
    yanchor="top",
    y=-0.2,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))

  st.plotly_chart(fig_box, theme='streamlit', use_container_width=True, height=200)

  


with tab2:
  acOrNot = list((mileage['车辆活跃度'].unique()))
  drive = list(mileage['驱动方式'].unique())
  col1, col2= st.columns(2, gap='large')
  x = col1.multiselect('选择车辆活跃度类型', acOrNot, key=21)
  y = col2.multiselect('驱动方式', drive, key=22)

  select = mileage
  if len(x)>0:
    select = mileage[(mileage['车辆活跃度'].isin(x))]
  if len(y)>0:
    select = mileage[(mileage['驱动方式'].isin(y))]

  fig_hist = px.histogram(select, x='里程区间', y='车辆数量', color='SOH')
  fig_hist.update_layout(legend=dict(
    yanchor="top",
    y=-0.4,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))
  fig_hist.update_layout(yaxis_title='车辆数量')
  st.plotly_chart(fig_hist, theme='streamlit', use_container_width=True, height=200)

  fig_box = px.box(select, x='里程区间', y='车辆数量', color='SOH')
  fig_box.update_layout(legend=dict(
    yanchor="top",
    y=-0.4,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))

  st.plotly_chart(fig_box, theme='streamlit', use_container_width=True, height=200)



with tab3:
  vehMaker = list((active['车辆厂商'].unique()))
  vehMaker.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  vehType = list(active['车辆类别'].unique())
  vehType.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  vehUse = list(active['车辆用途'].unique())
  vehUse.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  drive = list(active['驱动方式'].unique())
  drive.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  col1, col2,col3, col4= st.columns(4, gap='large')
  a = col1.multiselect('选择车辆厂商', vehMaker, key=31,)
  b = col2.multiselect('选择车辆类别', vehType, key=32)
  c = col3.multiselect('选择车辆用途', vehUse, key=33)
  d = col4.multiselect('选择驱动方式', drive, key=34)

  select = active

  for i,j in zip(['车辆厂商','车辆类别','车辆用途','驱动方式'], [a,b,c,d]):
    if len(j)>0:
      select = active[(active[i].isin(j))]

  fig_hist = px.histogram(select, x='车辆厂商', y='车辆数量', color='SOH', category_orders={'SOH':['50%-60%',	'60%-70%',	'70%-80%',	'80%-90%',	'90%-100%']})
  fig_hist.update_layout(legend=dict(
    yanchor="top",
    y=1.2,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))
  fig_hist.update_layout(yaxis_title='车辆数量')
  st.plotly_chart(fig_hist, theme='streamlit', use_container_width=True, height=200)

  col11, col22 = st.columns(2, gap='large')

  sumNumber = px.pie(select.groupby('车辆厂商')['车辆数量'].sum().reset_index(), names='车辆厂商', values='车辆数量',)
  col11.plotly_chart(sumNumber, theme='streamlit', use_container_width=True, height=200)


  sohNumber = px.pie(select.groupby('SOH')['车辆数量'].sum().reset_index(), names='SOH', values='车辆数量',category_orders={'SOH':['50%-60%',	'60%-70%',	'70%-80%',	'80%-90%',	'90%-100%']})
  col22.plotly_chart(sohNumber, theme='streamlit', use_container_width=True, height=200)



with tab4:
  vehMaker = list((inactive['车辆厂商'].unique()))
  vehMaker.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  vehType = list(inactive['车辆类别'].unique())
  vehType.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  vehUse = list(inactive['车辆用途'].unique())
  vehUse.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  drive = list(inactive['驱动方式'].unique())
  drive.sort(key=lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

  col1, col2,col3, col4= st.columns(4, gap='large')
  a = col1.multiselect('选择车辆厂商', vehMaker, key=41,)
  b = col2.multiselect('选择车辆类别', vehType, key=42)
  c = col3.multiselect('选择车辆用途', vehUse, key=43)
  d = col4.multiselect('选择驱动方式', drive, key=44)

  select = inactive

  for i,j in zip(['车辆厂商','车辆类别','车辆用途','驱动方式'], [a,b,c,d]):
    if len(j)>0:
      select = inactive[(inactive[i].isin(j))]

  fig_hist = px.histogram(select, x='车辆厂商', y='车辆数量', color='SOH', category_orders={'SOH':['50%-60%',	'60%-70%',	'70%-80%',	'80%-90%',	'90%-100%']})
  fig_hist.update_layout(legend=dict(
    yanchor="top",
    y=1.2,
    xanchor="center",
    x=0.5,
    orientation='h',valign='top', title=None
  ))
  fig_hist.update_layout(yaxis_title='车辆数量')
  st.plotly_chart(fig_hist, theme='streamlit', use_container_width=True, height=200)

  col11, col22 = st.columns(2, gap='large')

  sumNumber = px.pie(select.groupby('车辆厂商')['车辆数量'].sum().reset_index(), names='车辆厂商', values='车辆数量',)
  col11.plotly_chart(sumNumber, theme='streamlit', use_container_width=True, height=200)


  sohNumber = px.pie(select.groupby('SOH')['车辆数量'].sum().reset_index(), names='SOH', values='车辆数量',category_orders={'SOH':['50%-60%',	'60%-70%',	'70%-80%',	'80%-90%',	'90%-100%']})
  col22.plotly_chart(sohNumber, theme='streamlit', use_container_width=True, height=200)


