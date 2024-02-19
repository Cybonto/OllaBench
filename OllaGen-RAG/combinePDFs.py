import os
import PyPDF2

# Function to combine PDFs in a folder
def combine_pdfs(folder_path, output_pdf):
    pdf_merger = PyPDF2.PdfMerger()
    
    try:
        # List all PDF files in the folder
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        
        if len(pdf_files) == 0:
            print("No PDF files found in the folder.")
            return
        
        # Sort PDF files alphabetically
        pdf_files.sort()
        
        # Merge PDFs
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            pdf_merger.append(pdf_path)
        
        # Write the merged PDF to the output file
        pdf_merger.write(output_pdf)
        pdf_merger.close()
        
        print(f"PDFs in the folder have been successfully combined into '{output_pdf}'.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Input: Folder containing PDFs
pdf_folder = input("Enter the folder path containing PDFs: ")

# Input: Output PDF file name
output_pdf = input("Enter the name of the output PDF file: ")

combine_pdfs(pdf_folder, output_pdf)
