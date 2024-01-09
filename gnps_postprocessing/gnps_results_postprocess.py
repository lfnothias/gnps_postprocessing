
import pandas as pd
import numpy as np
import math

def gnps_filter_annotations(table_in, inchi_column, 
                            ionisation_mode='pos',  max_ppm_error=10, min_cosine=0.7, 
                            shared_peaks=6, max_spec_charge=2, prefix = ''):
        
        #Apply prefix to the column name of the gnps table if needed:
        if len(prefix)>2:
            new_names = [(i,str(prefix)+i) for i in table_in.iloc[:, 0:].columns.values]
            table_in.rename(columns = dict(new_names), inplace=True) 
            table = table_in
        else:
            table = table_in
            
        #Go for filtering    
        print('Initial number of annotations: '+str(table.shape[0]))
        #Filtering GNPS annotations
        table = table[table[prefix+'IonMode'].str.lower().str.startswith(str(ionisation_mode), na=False)] #check ionisation mode
        print('Remaining after ionisation mode filtering: '+str(table.shape[0]))
        table = table[table[prefix+'MZErrorPPM'] <= float(max_ppm_error)]
        print('Remaining after max_ppm_error filtering: '+str(table.shape[0]))
        table = table[table[prefix+'MQScore'] >= float(min_cosine)]
        print('Remaining after min_cosine filtering: '+str(table.shape[0]))
        table = table[table[prefix+'SharedPeaks'] > int(shared_peaks)]
        print('Remaining after number of shared_peaks filtering: '+str(table.shape[0]))
        table = table[table[prefix+'SpecCharge'] <= int(max_spec_charge)]
        print('Remaining after number of spectrum charge filtering: '+str(table.shape[0]))

        return table
    
    
def gnps_clean_up_annotations(table_in, inchi_column,  
                              remove_intrinsically_charged_mol = True, 
                              remove_C_containing_in_source_fragment = True,
                              prefix = '', must_have_structure = True):       
    
        #Apply prefix to the column name of the gnps table if needed:
        if len(prefix) > 2:
            new_names = [(i,str(prefix)+i) for i in table_in.iloc[:, 0:].columns.values]
            table_in.rename(columns = dict(new_names), inplace=True) 
            table = table_in
            print('Prefix added to column name')
        else:
            table = table_in
        
        #Filters
        print('Initial number of annotations: '+str(table.shape[0]))
        if must_have_structure is True:
            table = table[table[str(inchi_column)].notnull()]            
            print('After removing annotations without structure: '+str(table.shape[0]))
        if remove_intrinsically_charged_mol is True:
            table = table[~table[str(inchi_column)].str.contains('q:+|p+1|p+2|p-1', na=False)]
            print('After intrinsically charged molecules removed: '+str(table.shape[0]))
        if remove_C_containing_in_source_fragment is True:
            table = table[~table[str(prefix)+'Adduct'].str.contains("-C|i")]
            print('After carbon containing adducts filtering: '+str(table.shape[0]))
        
        return table

    
def get_molecular_formula_from_inchi(table_in, inchi_column, remove_C_containing_in_source_fragment = True, prefix = ''):
        
        #Apply prefix to the column name of the gnps table if needed:
        if len(prefix) > 2:
            new_names = [(i,str(prefix)+i) for i in table_in.iloc[:, 0:].columns.values]
            table_in.rename(columns = dict(new_names), inplace=True) 
            table = table_in
            print('Prefix added to column name')
        else:
            table = table_in
        
        #Filter 
        print('Initial number of annotations: '+str(table.shape[0]))
        
        if remove_C_containing_in_source_fragment is True:
            table = table[~table[str(prefix)+'Adduct'].str.contains("-C|i")]
            print('After carbon containing adducts filtering: '+str(table.shape[0]))

        #Get molecular formula
        table[str(prefix)+'INCHI_MF'] = table[str(inchi_column)].str.split("/",expand=False).str[1]
        
        #Just to check there was no weird InChI
        table = table[table[str(prefix)+'INCHI_MF'].str.upper().str.startswith('C', na=False)]

        return table