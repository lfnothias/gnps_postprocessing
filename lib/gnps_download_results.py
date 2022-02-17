import subprocess
import shlex
import zipfile
import os
import pandas as pd

def gnps_download_results(job_id, output_folder):
    # This function download GNPS molecular networking job results locally 
    # and detect if the job is classical or feature-based Molecular networking.
    # It then creates instances of the network and annotation tables.
    
    # Author: Louis-Felix Nothias 2021-2022
    
    # Demo: 
    #gnps_annotations = gnps_downloader(job_id = 'bbee697a63b1400ea585410fafc95723', output_folder = 'gnps_results')
    #gnps_annotations = gnps_downloader(job_id = '2047c735fc3546f7a3a32c78245edccf', output_folder = 'gnps_results_fbmn')

    # Base link to download GNPS job annotations
    gnps_download_link = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task="+job_id+"&view=view_all_annotations_DB"
    
    # Launch the download
    print('==================')
    print('This is the GNPS job link: https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task='+job_id)
    print("Downloading the following content: " + str(gnps_download_link))
    
    # Clearing local files
    subprocess.call(shlex.split('rm '+output_folder+'.zip'))
    cmd = 'curl -d "" '+gnps_download_link+' -o '+output_folder+'.zip'
    
    # Call the process and catch errors
    try:
        subprocess.call(shlex.split(cmd))
    except subprocess.CalledProcessError as e:
        print(e.output)
    
    # We are checking that the call resulted in a excepted zipfile (using size)
    try:
        b = os.path.getsize(output_folder+'.zip')
        if b > 10000:
            print('GNPS job results were succesfully downloaded as: '+output_folder+'.zip')
        elif b < 10000:
            print(' ==========> ERROR in the download -> check the job ID and/or job type')
    except:
        print(' ==========> ERROR in the download -> check the job ID and/or job type')
   
    # Extracting the downloaded zipfile into a folder
    subprocess.call(shlex.split('rm -r '+output_folder))
    with zipfile.ZipFile(str(output_folder+'.zip'),"r") as zip_ref:
        zip_ref.extractall(output_folder)
    if os.path.isdir(output_folder) == True:
        print('GNPS job results were succesfully extracted into the folder: '+ str(output_folder))
    else:
        print(' ==========> ERROR in the download/extraction process')
        
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
            print('      '+str(df_annotations.shape[0]-1)+' spectral library annotations in the job.')

            path_networkinfo = [x for x in os.listdir(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID')][0]
            df_network = pd.read_csv(output_folder+'/clusterinfosummarygroup_attributes_withIDs_withcomponentID/'+path_networkinfo, sep='\t')
            print('==================')
            print('      '+str(df_network.shape[0]-1)+' nodes in the network (including single nodes).')
            
    gnps_download_results.df_network = df_network
    gnps_download_results.df_annotations = df_annotations