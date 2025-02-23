import streamlit as st #so now everytime i want to call streamlit, i can just call st
import pandas as pd #same
import os #this is for the files
from io import BytesIO #this is gonna allow our files to convert to binary and keep them temporarily in our memory for converting the files

# App Configuration - MUST BE FIRST!
st.set_page_config(
    page_title="💿 Data Sweeper",
    layout='wide',
    initial_sidebar_state="expanded"
)

# Updated CSS with better text visibility
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        color: #000000;
    }
    .stTitle {
        color: #FFFFFF !important;
        font-size: 3rem !important;
        padding-bottom: 2rem;
    }
    .stSubheader {
        color: #FFFFFF !important;
        padding-top: 1.5rem;
        padding-bottom: 0.5rem;
    }
    div[data-testid="stFileUploader"] {
        padding: 1rem;
        border: 2px dashed #1E88E5;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
    }
    div.stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0D47A1;
        border: none;
    }
    .stCheckbox {
        padding: 1rem 0;
        color: #FFFFFF;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem;
        color: #FFFFFF;
    }
    div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF;
    }
    .stRadio > label {
        color: #FFFFFF;
    }
    .stMultiSelect > label {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

#set up our app
st.title("💿 Data Sweeper")
st.markdown("""
    <div style='background-color: #E3F2FD; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; color: #800000  ;'>
        Transform your files between CSV and Excel formats with built-in data cleaning and visualization.
    </div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload your files (CSV or Excel)", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        # Create an expander for each file
        with st.expander(f"📁 Process {file.name}", expanded=True):
            file_ext = os.path.splitext(file.name)[-1].lower() #extract the extension of the file (is it csv or excel?)

            try:
                #read the file in the state of pandas data frame
                if file_ext == ".csv":
                    df = pd.read_csv(file)
                elif file_ext == ".xlsx":
                    df = pd.read_excel(file)
                else:
                    st.error(f"Unsupported file type: {file_ext}") 
                    #if that happens, continue checking the next file
                    continue

                #displayy info about the file
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{file.size/1024:.2f} KB")
                with col2:
                    st.metric("Rows", df.shape[0])
                with col3:
                    st.metric("Columns", df.shape[1])

                #show 5 rows of our df
                st.subheader("📊 Data Preview")
                st.dataframe(df.head(), use_container_width=True) #this is gonna show the first 5 rows of the data frame

                #Options for data cleaning
                st.subheader("🧹 Data Cleaning")
                if st.checkbox(f"Clean Data for {file.name}"):
                    clean_col1, clean_col2 = st.columns(2)  #this is gonna create first 2 coloumns

                    #with is our context manager, this is gonna allow us to do some operations and then automatically close the file
                    with clean_col1:
                        if st.button(f"Remove duplicates from {file.name}", key=f"dup_{file.name}"):
                            initial_rows = len(df)
                            df.drop_duplicates(inplace=True)
                            removed = initial_rows - len(df)
                            st.success(f"Removed {removed} duplicate rows!")

                    with clean_col2:
                        if st.button(f"Fill missing values for: {file.name}", key=f"fill_{file.name}"):
                            numeric_cols = df.select_dtypes(include=['number']).columns #this is gonna select all the numeric columns, it only applies to colomns with the numbers
                            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean()) #this is gonna fill the missing values with the mean of the column
                            st.success("Missing values have been filled!")

                #Choose specific columns to keep or convert
                st.subheader("📋 Column Selection")
                columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns) #df.columns will give the multiselect to all the colomns
                df = df[columns]

                #Create somee visualizations
                st.subheader("📈 Data Visualization")
                if st.checkbox(f"Show visualization for {file.name}"): #if user clicks on the box, then we are gonna show the visualization
                    numeric_df = df.select_dtypes(include='number')
                    if not numeric_df.empty:
                        st.bar_chart(numeric_df.iloc[:,:2], use_container_width=True)
                    else:
                        st.info("No numeric columns available for visualization")

                #Convert the file -> CSV to Excel or vice versa
                #This is gonna be on the new page
                st.subheader("🔄 Convert & Download")
                col1, col2 = st.columns([1, 2])
                with col1:
                    conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"conv_{file.name}") #this is gonna give us the radio button
                
                with col2:
                    buffer = BytesIO() #bytesio is a class and we are making an object that will create a buffer in memory for my file (for temparory storage)
                    if conversion_type == "CSV":
                        df.to_csv(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".csv")
                        mime_type = "text/csv"
                    elif conversion_type == "Excel":
                        df.to_excel(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".xlsx")
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                    #Download Button
                    st.download_button(
                        label=f"⬇️ Download {file.name} as {conversion_type}",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type,
                        key=f"download_{file.name}"
                    )

            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")

    st.success("✨ All files processed successfully!")
else:
    # Show welcome message when no files are uploaded
    st.info("👆 Upload your files above to get started!")