import streamlit as st
import w4h

def main():
    st.set_page_config(page_title='W4H WebApp',
                       page_icon=":material/globe_book:",
                       layout='wide',
                       initial_sidebar_state='expanded',
                       menu_items={"Get Help":'https://github.com/RJbalikian/wells4hydrogeology/wiki',
                                    "Report a bug":"https://github.com/RJbalikian/wells4hydrogeology/issues",
                                    'About':"W4H is a collaboration between the Illinois State Water Survey and the Illinois State Geological Survey"})
    with st.sidebar:
        runColBlank, runCol = st.columns([0.7, 0.3])
        runCol.button('Run Analysis', type='primary')

        st.header("Specify Input Data")
        with st.expander("Well Data", expanded=True):
            st.file_uploader(label='Upload Point File', key='point_file')

        with st.expander("Raster Data", expanded=True):
            st.header('Raster Data')
            surfTab, brtab = st.tabs(["Surface Raster", "Bedrock Raster"])
            SEFileTab, SEServTab = surfTab.tabs(['File', 'Service'])
            SEFileTab.file_uploader(label='Upload Surface Elevation')

            SEServTab.radio(label='Predefined Services', options=['GMRT', 'IL Lidar', "None"], horizontal=True,
                            key='pre_service')
            servTextDisabled = False
            if st.session_state.pre_service != 'None':
                servTextDisabled = True
            SEServTab.text_input(label='Enter Service URL (currenly on WMS supported)',
                                disabled=servTextDisabled)

        with st.expander("Extent and Resolution"):
            
            st.file_uploader(label='Study Area File', key='study_area')
            st.pills("Model Grid", options=["Upload Raster", "# Nodes", "Node Resolution"], default="# Nodes", key='model_type')
            if st.session_state.model_type == "Upload Raster":
                st.file_uploader(label='ModelGrid', key='model_grid')
            else:
                xnodecol, ynodecol = st.columns([0.5, 0.5])
                xnodeLabel = 'No. X Nodes'
                ynodeLabel = 'No. Y Nodes'
                if st.session_state.model_type == 'Node Resolution':
                    xnodeLabel = 'X Node Resolution'
                    ynodeLabel = 'Y Node Resolution'

                xnodecol.number_input(xnodeLabel, min_value=5, max_value=5000,
                                      step=1, value=100)
                ynodecol.number_input(ynodeLabel, min_value=5, max_value=5000,
                                      step=1, value=100)
        
        with st.expander("Data Mapping", expanded=True):
            widcol, descol = st.columns([0.5, 0.5])
            widcol.selectbox(label="Well ID Column", options=['API_NUMBER'], 
                            help="Select name of column from point file containing unique well ID's", key='well_id_col')
            descol.selectbox(label="Description Column", options=['FORMATION'], 
                            help="Select name of column from point file containing lithologic descriptions", key='description_col')

            xcol, ycol, zcol = st.columns([0.3, 0.3, 0.3])
            xcol.selectbox(label="X Coord Column", options=['LONGITUDE'])
            ycol.selectbox(label="Y Coord Column", options=['LATITUDE'])
            zcol.selectbox(label="Elevation Column", options=['SURFACE_ELEV'])

            tcol, bcol = st.columns([0.5, 0.5])
            tcol.selectbox(label="Top Column", options=['TOP', '2'])
            bcol.selectbox(label="Bottom Column", options=['BOTTOM', '2'])

        with st.expander("Additional Settings"):
            wellSetTab, surfElevSetTab, botSetTab = st.tabs(["WellData", "Surface Elevation", "Bottom Layer"])

if __name__ == "__main__":
    main()
