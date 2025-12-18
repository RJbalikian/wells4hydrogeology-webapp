import inspect
import io

import pandas as pd
import pyproj
import rioxarray as rxr
import streamlit as st
import w4h
import xarray as xr

CRS_LIST = pyproj.database.query_crs_info()
CRS_STR_LIST = [f"{crs.name} ({crs.auth_name}:{crs.code})" for crs in CRS_LIST]
CRS_DICT = {f"{crs.name} ({crs.auth_name}:{crs.code})": crs for crs in CRS_LIST}
IL_LIDAR_URL=r"https://data.isgs.illinois.edu/arcgis/services/Elevation/IL_Statewide_Lidar_DEM_WGS/ImageServer/WMSServer?request=GetCapabilities&service=WMS"
GMRT_BASE_URL = r"https://www.gmrt.org:443/services/GridServer?minlongitude&maxlongitude%2C%20&minlatitude&maxlatitude&format=geotiff&resolution=default&layer=topo"

DEFAULT_POINTS_CRS = "WGS 84 (EPSG:4326)"
DEFAULT_POINTS_CRS_INDEX = CRS_STR_LIST.index(DEFAULT_POINTS_CRS)

def get_defaults():
    w4h_funs = [w4h.file_setup, w4h.read_raw_csv, w4h.define_dtypes, w4h.merge_metadata, w4h.coords2geometry,
                w4h.read_study_area, w4h.clip_gdf2study_area, w4h.read_grid, w4h.add_control_points,
                w4h.remove_nonlocated, w4h.remove_no_topo, w4h.remove_no_depth, w4h.remove_bad_depth, w4h.remove_no_description,
                w4h.get_search_terms, w4h.read_dictionary_terms, w4h.specific_define, 
                w4h.split_defined, w4h.start_define, w4h.wildcard_define, w4h.remerge_data, w4h.fill_unclassified,
                w4h.read_lithologies, w4h.merge_lithologies, 
                w4h.align_rasters, w4h.get_drift_thick, w4h.sample_raster_points, w4h.get_layer_depths, w4h.layer_target_thick,
                w4h.layer_interp, w4h.export_grids]
    
    fullParamList = []
    fullDefaultList = []
    paramDefaultDict = {}
    for func in w4h_funs:
        parameters = inspect.signature(func).parameters
        defaults = [param.default for param in list(zip(*parameters.items()))[1]]
        parameters = list(zip(*parameters.items()))[0]
        fullParamList.extend(parameters)
        fullDefaultList.extend(defaults)

        for i, p in enumerate(parameters):
            paramDefaultDict[p] = defaults[i]
    return paramDefaultDict

st.session_state.param_defaults = get_defaults()
    
def w4hrun():
    stss = st.session_state
    st.toast('Processing')

    specified_params = ['well_data', 'surf_elev_grid', 'bedrock_elev_grid', 'model_grid']
    # Code to read in well_data file
    # FIX THIS
    well_data = pd.read_csv(stss.well_data)

    if stss.surf_raster_type == 'File':
        pass
        # Code to read in file
        stss.surf_elev_grid = None
    else:
        # Code to read in service
        pass
        stss.surf_elev_grid = None

    # Code to read in lower surface elevation
    # Fix this to get it working with actual file, not just text
    stss.bedrock_elev_grid = rxr.open_rasterio(stss.lower_rast_TEXT)

    # Get model grid
    if 'node' in str(stss.model_type).lower():
        # FIX code to generate model grid from node spacing or number
        pass
    elif stss.model_type == 'Surface Elevation':
        # CODE TO READ SURFACE ELEVATION
        pass
    elif stss.model_type == 'Lower Surface':
        # CODE TO READ SURFACE ELEVATION
        pass
    else:
        stss.model_grid_TEXT
    
def main():
    st.set_page_config(page_title='W4H WebApp',
                       page_icon=":material/globe_book:",
                       layout='wide',
                       initial_sidebar_state='expanded',
                       menu_items={"Get Help":'https://github.com/RJbalikian/wells4hydrogeology/wiki',
                                    "Report a bug":"https://github.com/RJbalikian/wells4hydrogeology/issues",
                                    'About':"W4H is a collaboration between the Illinois State Water Survey and the Illinois State Geological Survey"})
    with st.sidebar:
        sampleCol, headerCol  = st.columns([0.7, 0.3], vertical_alignment='top')
        with headerCol.container(horizontal_alignment='right'):
            st.button('Run Analysis', type='primary', on_click=w4hrun)
        with sampleCol.container(horizontal_alignment='right'):
            st.checkbox('Demo run', disabled=True, value=False)
        st.header("Specify Input Data", divider='rainbow')
        

        with st.expander("Well Data", expanded=True):
            wdval = None
            if hasattr(st.session_state, 'point_file') and st.session_state.point_file is not None:
                wdval = st.session_state.point_file.name
            st.text_input(label="Well data file", value=wdval, key='well_data')
            st.file_uploader(label='Upload Point File', key='point_file')

        with st.expander("Raster Data", expanded=True):
            st.header('Raster Data')
            surfTab, brtab = st.tabs(["Surface Raster", "Lower Raster"])
            surfTab.segmented_control(label='Select Raster Type', options=['File', 'Web Service'], 
                                      key='surf_raster_type', default='Web Service')
            if st.session_state.surf_raster_type == 'File':
                srval = None
                if hasattr(st.session_state, 'surf_rast_ul') and st.session_state.surf_rast_ul is not None:
                    srval = st.session_state.surf_rast_ul.name
                surfTab.text_input(label="Surface Raster file", value=srval)
                surfTab.file_uploader(label='Upload Surface Elevation Raster', key='surf_rast_ul')

            else:
                surfTab.radio(label='Surface Raster Services', options=['GMRT', 'IL Lidar', "Custom"], horizontal=True,
                            key='pre_service')
                servTextDisabled = False
                if st.session_state.pre_service != 'Custom':
                    servTextDisabled = True
                surfTab.text_input(label='Enter Service URL (currenly only WMS supported)',
                                    disabled=servTextDisabled)
            specSurfRastCol, surfRastCRSCol = surfTab.columns([0.3, 0.7])
            specSurfRastCol.toggle('Specify Raster CRS', key='specify_surfrast_crs')

            surfRastCRSDisabled =  not st.session_state.specify_surfrast_crs
            surfRastCRSCol.selectbox("Surface Raster CRS", disabled = surfRastCRSDisabled,
                              options=CRS_STR_LIST, index=DEFAULT_POINTS_CRS_INDEX, 
                              key='surf_raster_CRS')

            # Bedrock raster
            brval = None
            if hasattr(st.session_state, 'lower_rast_UL') and st.session_state.lower_rast_UL is not None:
                brval = st.session_state.lower_rast_UL.name
            brtab.text_input(label="Lower Raster file", value=brval, key='lower_rast_TEXT')
            brtab.file_uploader(label='Upload Lower Elevation Raster', key='lower_rast_UL')

        with st.expander("Extent and Resolution"):
            st.file_uploader(label='Study Area File', key='study_area')
            st.header('Model Grid')
            st.selectbox("Model Grid Source", 
                    options=["Lower Surface", "Surface Elevation",
                             "Raster Upload", "# Nodes", "Node Resolution"],
                     index=0, key='model_type')
            if 'node' not in st.session_state.model_type.lower():
                if st.session_state.model_type == 'Raster Upload':
                    mgval = None
                    if hasattr(st.session_state, 'model_grid_UL') and st.session_state.model_grid_UL is not None:
                        mgval = st.session_state.model_grid_UL.name
                    st.text_input(label='Model Grid File', value=mgval, key='model_grid_TEXT')
                    st.file_uploader(label='ModelGrid', key='model_grid_UL')
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
