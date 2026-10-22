"""Run: python dash_app.py   |   Open: http://127.0.0.1:8050"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State, ctx
from model import simulate, sample, propagated_voltage, T_END, STIM_START, STIM_END

dash_app = Dash(__name__)
dash_app.title = 'Stimulus to Signal | Dynamic Scientific Story'

FIG = dict(margin=dict(l=48,r=25,t=36,b=48), paper_bgcolor='#fff', plot_bgcolor='#fffdf7', font=dict(color='#493a46',size=12))
BLUE, PINK, GOLD, PURPLE = '#a84577', '#e7a3bd', '#bd8a18', '#81566e'

def chart(title, height=340):
    f=go.Figure()
    f.update_layout(title=dict(text=title,font=dict(size=17)),height=height,**FIG)
    return f

def section(n, label, question, graph_id, note):
    return html.Section(className='view', children=[html.H2(f'{n}. {label}'),html.P(question,className='question'),dcc.Graph(id=graph_id,config={'displaylogo':False}),html.P(note,className='note')])

dash_app.layout=html.Main([
    html.H1('Stimulus → Signal'),
    html.P('An interactive scientific story of neural excitation and propagation · Hodgkin–Huxley point-membrane model',className='subtitle'),
    html.Div(className='controls',children=[
        html.Div([html.Label('Stimulus intensity (µA/cm²)'),dcc.Slider(0,25,1,value=12,id='stim',marks={0:'0',5:'5',10:'10',15:'15',20:'20',25:'25'},tooltip={'placement':'bottom','always_visible':True})]),
        html.Div([html.Label('Sodium maximum conductance (fraction)'),dcc.Slider(.2,1.2,.1,value=1,id='na',marks={.2:'0.2×',.6:'0.6×',1:'1×',1.2:'1.2×'})]),
        html.Div([html.Label('Potassium maximum conductance (fraction)'),dcc.Slider(.2,1.2,.1,value=1,id='k',marks={.2:'0.2×',.6:'0.6×',1:'1×',1.2:'1.2×'})]),
        html.Div([html.Label('Time (ms)'),dcc.Slider(0,40,.25,value=0,id='time',tooltip={'placement':'bottom','always_visible':True}),html.Div([html.Button('▶ Play',id='play'),html.Button('Step +0.5 ms',id='step'),html.Button('Reset',id='reset')],className='buttons')]),
        dcc.Interval(id='tick',interval=160,n_intervals=0,disabled=True),
        html.Div(id='readout',className='readout')
    ]),
    section(1,'The stimulus','What changes when a neuron receives electrical input?', 'v1','The current pulse is applied from 5 to 8 ms. Adjust stimulus to see input strength change.'),
    section(2,'Membrane voltage & excitation','Which stimulus strengths trigger a full electrical spike?', 'v2','The dotted −55 mV line is a visual reference, NOT a hard threshold switch in the Hodgkin–Huxley equations.'),
    section(3,'Sodium and potassium mechanisms','How do channel conductances and currents change with voltage?', 'v3','In the current convention, negative Na⁺ current is inward; positive K⁺ current is outward.'),
    section(4,'Anatomy of the action potential','What is happening during the rising, falling, and recovery stages?', 'v4','Phase labels use the local voltage trend for explanation; they are not separate model states.'),
    section(5,'Propagation along the axon','How can a traveling waveform appear across different positions?', 'v5','Illustrative propagation = delayed copies of the point-membrane waveform at 0.4 mm/ms; NOT a biophysical spatial cable simulation.'),
    html.Section(className='view',children=[html.H2('6. Compare conditions'),html.P('How does changing stimulus intensity or sodium conductance alter firing?',className='question'),html.Label('Compare current settings with:'),dcc.Dropdown(id='comparison',options=[{'label':'Zero stimulus (boundary case)','value':'zero'},{'label':'Weak stimulus (2 µA/cm²)','value':'weak'},{'label':'Strong stimulus (20 µA/cm²)','value':'strong'},{'label':'Reduced Na⁺ conductance (50%)','value':'sodium'}],value='weak',clearable=False),dcc.Graph(id='v6',config={'displaylogo':False}),html.P('Both scenarios use identical scales so differences are not exaggerated.',className='note')]),
    html.Section(className='view',children=[html.H2('Model and limitations'),html.P('Standard Hodgkin–Huxley (1952) squid giant axon conductance equations are integrated with fixed-step fourth-order Runge–Kutta (0.025 ms). The stimulus pulse runs 5–8 ms. The sodium and potassium gates evolve continuously, not by a manually applied voltage threshold.'),html.P('This is simulated educational data, not measured neurons. The propagation view is an illustrative traveling-wave approximation, so it cannot predict conduction velocity or effects of myelination. See README.md and verify.py for equations, units, reproducibility, and checks.'),html.P('Sources: Hodgkin & Huxley (1952), Journal of Physiology, DOI 10.1113/jphysiol.1952.sp004764; Purves et al., Neuroscience (2001).')]),
    html.Footer('Python · NumPy · Plotly · Dash | Original six-view scientific simulation')
])

@dash_app.callback(Output('tick','disabled'),Output('play','children'),Input('play','n_clicks'),State('tick','disabled'),prevent_initial_call=True)
def toggle(_, disabled):
    return not disabled, '▶ Play' if not disabled else '⏸ Pause'

@dash_app.callback(Output('time','value'),Input('tick','n_intervals'),Input('step','n_clicks'),Input('reset','n_clicks'),State('time','value'),prevent_initial_call=True)
def advance(_, __, ___, time):
    triggered=ctx.triggered_id
    if triggered=='reset': return 0
    if triggered=='step': return round(min(T_END,time+.5),2)
    if triggered=='tick': return round(0 if time>=T_END else min(T_END,time+.25),2)
    return time

@dash_app.callback([Output(f'v{i}','figure') for i in range(1,7)]+[Output('readout','children')],
              Input('stim','value'),Input('na','value'),Input('k','value'),Input('time','value'),Input('comparison','value'))
def update_all(stim,na,k,time,compare):
    d=simulate(float(stim),float(na),float(k)); s=sample(d,time); t=d['t']; v=d['V'];
    fired=bool(np.max(v)>0)
    # View 1: timed applied current alongside a physically oriented simplified neuron.
    f1=make_subplots(rows=2,cols=1,row_heights=[.57,.43],vertical_spacing=.15,subplot_titles=('Neuron schematic: current input → axon','Applied stimulus current (µA/cm²)'))
    f1.add_trace(go.Scatter(x=[0,1.3,2.9,4.8],y=[0,0,0,0],mode='lines',line=dict(width=20,color='#f1bed1'),hoverinfo='skip',showlegend=False),row=1,col=1)
    f1.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(size=65,color='#f7c9da',line=dict(color=BLUE,width=3)),name='Soma',hovertemplate='Cell body<extra></extra>'),row=1,col=1)
    f1.add_trace(go.Scatter(x=[.25],y=[.36],mode='markers+text',marker=dict(size=17+stim,color=PINK),text=['Stimulus'],textposition='top center',name='Current input',hovertemplate=f'Input intensity: {stim} µA/cm²<extra></extra>'),row=1,col=1)
    f1.add_trace(go.Scatter(x=[4.8],y=[0],mode='markers',marker=dict(size=25,color=GOLD),name='Terminal'),row=1,col=1)
    f1.add_trace(go.Scatter(x=t,y=d['I_stim'],line=dict(color=PINK,width=3),name='Current pulse',hovertemplate='%{x:.2f} ms<br>%{y:.2f} µA/cm²<extra></extra>'),row=2,col=1)
    f1.add_vline(x=time,line_dash='dash',line_color=PURPLE,row=2,col=1)
    f1.update_xaxes(visible=False,range=[-.7,5.5],row=1,col=1);f1.update_yaxes(visible=False,range=[-.65,.8],row=1,col=1)
    f1.update_xaxes(title_text='Time (ms)',row=2,col=1);f1.update_yaxes(title_text='µA/cm²',row=2,col=1)
    f1.update_layout(height=370,showlegend=False,**FIG)
    # View 2: fixed axis truthfully compares magnitudes.
    f2=chart('Voltage trace and reference region')
    f2.add_trace(go.Scatter(x=t,y=v,mode='lines',line=dict(color=BLUE,width=3),name='Membrane potential',hovertemplate='%{x:.2f} ms<br>%{y:.2f} mV<extra></extra>'))
    f2.add_hline(y=-55,line_dash='dot',line_color=GOLD,annotation_text='~−55 mV reference')
    f2.add_vline(x=time,line_dash='dash',line_color=PURPLE)
    f2.add_trace(go.Scatter(x=[time],y=[s['V']],mode='markers',marker=dict(size=12,color=PINK),name='Current state'))
    f2.update_xaxes(title='Time (ms)',range=[0,40]);f2.update_yaxes(title='Voltage (mV)',range=[-90,60]);
    # View 3: independent conductances and ionic currents.
    f3=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.13,subplot_titles=('Conductance (mS/cm²)','Ionic current density (µA/cm²)'))
    for key,color,label,row in [('gNa',PINK,'gNa (Na⁺)',1),('gK',BLUE,'gK (K⁺)',1),('INa',PINK,'INa (Na⁺)',2),('IK',BLUE,'IK (K⁺)',2)]:
        f3.add_trace(go.Scatter(x=t,y=d[key],name=label,line=dict(color=color,width=2),hovertemplate='%{x:.2f} ms<br>%{y:.2f}<extra>'+label+'</extra>'),row=row,col=1)
        f3.add_vline(x=time,line_dash='dash',line_color=PURPLE,row=row,col=1)
    f3.update_xaxes(title_text='Time (ms)',row=2,col=1);f3.update_layout(height=520,legend=dict(orientation='h',y=1.12),**FIG)
    # View 4: moving time cursor and text phase.
    dv=np.gradient(v,t); idx=int(np.clip(round(time/.025),0,len(t)-1))
    if time < STIM_START: phase='Resting'
    elif v[idx]>0 and dv[idx] > -10: phase='Near peak'
    elif dv[idx]>5: phase='Depolarization'
    elif dv[idx]<-5 and v[idx]>-65: phase='Repolarization'
    elif v[idx]<-68: phase='After-hyperpolarization'
    else: phase='Recovery / resting'
    f4=chart(f'Current phase: {phase}')
    f4.add_trace(go.Scatter(x=t,y=v,line=dict(color='#e6cfd9',width=3),name='Complete waveform'))
    f4.add_trace(go.Scatter(x=t[:idx+1],y=v[:idx+1],line=dict(color=PURPLE,width=4),name='Elapsed waveform'))
    f4.add_trace(go.Scatter(x=[time],y=[s['V']],mode='markers',marker=dict(color=PINK,size=13),name='Current state',hovertemplate='t=%{x:.2f} ms; V=%{y:.2f} mV<extra></extra>'))
    f4.update_xaxes(title='Time (ms)',range=[0,40]);f4.update_yaxes(title='Membrane voltage (mV)',range=[-90,60]);
    # View 5: spatially shifted waveform (illustrative only).
    positions=np.linspace(0,4,81)
    z=np.array([propagated_voltage(d,positions,tt) for tt in np.linspace(0,40,101)])
    f5=make_subplots(rows=2,cols=1,vertical_spacing=.15,row_heights=[.7,.3],subplot_titles=('Space–time voltage (mV)','Voltage along axon at selected time'))
    f5.add_trace(go.Heatmap(x=positions,y=np.linspace(0,40,101),z=z,colorscale='RdBu_r',zmin=-90,zmax=50,colorbar=dict(title='mV'),hovertemplate='x=%{x:.2f} mm<br>t=%{y:.2f} ms<br>V=%{z:.1f} mV<extra></extra>'),row=1,col=1)
    f5.add_hline(y=time,line_color='black',line_dash='dash',row=1,col=1)
    vs=propagated_voltage(d,positions,time)
    f5.add_trace(go.Scatter(x=positions,y=vs,fill='tozeroy',line=dict(color=PURPLE,width=3),name='Spatial voltage',hovertemplate='x=%{x:.2f} mm<br>V=%{y:.1f} mV<extra></extra>'),row=2,col=1)
    f5.update_xaxes(title_text='Axon position (mm)',row=2,col=1);f5.update_yaxes(title_text='Time (ms)',row=1,col=1);f5.update_yaxes(title_text='Voltage (mV)',range=[-90,60],row=2,col=1)
    f5.update_layout(height=540,showlegend=False,**FIG)
    # View 6: current versus alternative, same axis scale.
    if compare=='zero': other=simulate(0,1,1); name='No stimulus (0 µA/cm²)'
    elif compare=='weak': other=simulate(2,1,1);name='Weak (2 µA/cm²)'
    elif compare=='strong': other=simulate(20,1,1);name='Strong (20 µA/cm²)'
    else: other=simulate(float(stim),.5,float(k));name='Na⁺ conductance = 0.5×'
    f6=chart('Current selection vs. comparison condition',height=375)
    f6.add_trace(go.Scatter(x=t,y=d['V'],name='Your settings',line=dict(color=BLUE,width=3)))
    f6.add_trace(go.Scatter(x=t,y=other['V'],name=name,line=dict(color=PINK,width=2,dash='dash')))
    f6.add_vline(x=time,line_color=PURPLE,line_dash='dot')
    f6.update_xaxes(title='Time (ms)',range=[0,40]);f6.update_yaxes(title='Membrane voltage (mV)',range=[-90,60])
    values=f'Time {time:.2f} ms | Membrane {s["V"]:.2f} mV | Na⁺ current {s["INa"]:.2f} µA/cm² | K⁺ current {s["IK"]:.2f} µA/cm² | Spike in simulation: {"Yes" if fired else "No"}'
    return f1,f2,f3,f4,f5,f6,values

# Expose the underlying Flask WSGI application to Vercel.
app = dash_app.server

if __name__=='__main__':
    dash_app.run(debug=False,port=8050)
