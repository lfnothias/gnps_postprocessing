import subprocess
import shlex
import zipfile
import os
import pandas as pd
import requests
import shutil

def gnps_download_results(job_id, output_folder, force_redownload='yes'):
    # This function download GNPS molecular networking job results locally 
    # and detect if the job is classical or feature-based Molecular networking.
    # It then creates instances of the network and annotation tables.
    
    # Author: Louis-Felix Nothias 2021-2022
    
    # Demo: 
    #gnps_annotations = gnps_downloader(job_id = 'bbee697a63b1400ea585410fafc95723', output_folder = 'gnps_results')
    #gnps_annotations = gnps_downloader(job_id = '2047c735fc3546f7a3a32c78245edccf', output_folder = 'gnps_results_fbmn')
    
    # Base link to download GNPS job annotations
    gnps_download_link = f"https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task={job_id}&view=view_all_annotations_DB"
    output_zip = f"{output_folder}.zip"

    # Check if the ZIP file and the extracted folder already exist
    if os.path.exists(output_zip) and os.path.isdir(output_folder) and force_redownload.lower() != 'yes':
        #print('Using already downloaded and extracted GNPS results')
        pass
    else:
        # Remove existing ZIP file if it exists
        if os.path.exists(output_zip):
            try:
                os.remove(output_zip)
            except OSError as e:
                print(f"Error deleting file: {output_zip}. Error: {e}")

    # Download the file using requests
    try:
        with requests.post(gnps_download_link, data={}, stream=True) as r:  # Changed to POST request
            r.raise_for_status()
            with open(output_zip, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        #print(f"Downloaded file: {output_zip}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
    except Exception as e:
        print(f"Error in downloading file: {e}")
    
    # Check if the download was successful
    if not os.path.exists(output_zip):
        print("==========> ERROR in the download -> check the job ID and/or job type")
        
    # Check the size of the downloaded file
    try:
        file_size = os.path.getsize(output_zip)
        if file_size > 10000:
            #print(f'GNPS job results were successfully downloaded as: {output_zip}')
            pass
        else:
            print('==========> ERROR in the download -> check the job ID and/or job type')
    except OSError as e:
        print(f'Error checking file size: {e}')

    #removing the folder if already exists
    if os.path.exists(output_folder):
        try:
            shutil.rmtree(output_folder)
        except Exception as e:
            print(f"Error removing existing folder: {e}")
    else:
        pass

    # Extracting the downloaded zipfile into a folder
    try:
        with zipfile.ZipFile(output_zip, "r") as zip_ref:
            zip_ref.extractall(output_folder)
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid ZIP file.")
    except FileNotFoundError:
        print(f"Error: The file {output_zip} does not exist.")
    except Exception as e:
        print(f"Unexpected error during extraction: {e}")
    # Check if files were successfully extracted
    if any(os.scandir(output_folder)):
        #print(f'Files were successfully extracted into the folder: {output_folder}')
        pass
    else:
        print('==========> ERROR in the extraction process')
        
    # We are gonna check if this is classical molecular networking job
    try :
        path = [x for x in os.listdir(output_folder+'/result_specnets_DB')][0]
        df_annotations  = pd.read_csv(output_folder+'/result_specnets_DB/'+path, sep='\t')
        print('==================')
        print('   CLASSICAL MOLECULAR NETWORKING job detected')
        print('==================')
        print('      '+str(df_annotations.shape[0]-1)+' spectral library annotations in the job.')

        path_networkinfo = [x for x in os.listdir(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID')][0]
        df_network = pd.read_csv(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID/'+path_networkinfo, sep='\t')
        print('==================')
        print('      '+str(df_network.shape[0]-1)+' nodes in the network (including single nodes)')
        
    # If it is not a classical molecular networking job, we try feature-based molecular networking
    except : 
    
        # We try for more recent version of the FBMN workflow
        try: 
            print('==================')
            path = [x for x in os.listdir(output_folder+'/DB_result')][0]
            df_annotations = pd.read_csv(output_folder+'/DB_result/'+path, sep='\t')
            print('==================')
            print('   FEATURE-BASED MOLECULAR NETWORKING job detected - Version > 28')
            print('==================')
            print('      '+str(df_annotations.shape[0]-1)+' spectral library annotations in the job.')

            path_networkinfo = [x for x in os.listdir(output_folder+'/clusterinfo_summary')][0]
            df_network = pd.read_csv(output_folder+'/clusterinfo_summary/'+path_networkinfo, sep='\t')
            print('==================')
            print('      '+str(df_network.shape[0]-1)+' nodes in the network (including single nodes).')
        
        # We fall back to older version of the FBMN workflow
        except:
            print('==================')
            path = [x for x in os.listdir(output_folder+'/DB_result')][0]
            df_annotations = pd.read_csv(output_folder+'/DB_result/'+path, sep='\t')
            print('==================')
            print('   FEATURE-BASED MOLECULAR NETWORKING job detected - Version < 28')
            print('==================')
            #print('      '+str(df_annotations.shape[0]-1)+' spectral library annotations in the job.')

            path_networkinfo = [x for x in os.listdir(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID')][0]
            df_network = pd.read_csv(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID/'+path_networkinfo, sep='\t')
            print('==================')
            #print('      '+str(df_network.shape[0]-1)+' nodes in the network (including single nodes).')
            
    gnps_download_results.df_network = df_network
    gnps_download_results.df_annotations = df_annotations
