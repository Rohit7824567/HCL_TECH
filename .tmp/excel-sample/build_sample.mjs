import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const source='data/sample_dataset.csv';
const outputDir='outputs/sample-data-2026-11-21';
const sourceText=await fs.readFile(source,'utf8');
const workbook=await Workbook.fromCSV(sourceText,{sheetName:'Transactions'});
const sheet=workbook.worksheets.getItem('Transactions');
const recordCount=sourceText.trim().split(/\r?\n/).length-1;
const lastRow=recordCount+1;
const records=sheet.getRange(`A2:K${lastRow}`).values;
for(const row of records){row[7]=new Date(`${row[7]}T00:00:00`);row[8]=Number(row[8]);row[9]=Number(row[9]);}
sheet.getRange(`A2:K${lastRow}`).values=records;
sheet.showGridLines=false;
sheet.freezePanes.freezeRows(1);
sheet.getRange(`A1:K${lastRow}`).format.font={name:'Arial',size:10,color:'#3B3024'};
sheet.getRange('A1:K1').format={fill:'#402B1C',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},verticalAlignment:'center',wrapText:true};
sheet.getRange('A1:K1').format.rowHeight=28;
sheet.getRange(`H2:H${lastRow}`).format.numberFormat='yyyy-mm-dd';
sheet.getRange(`I2:I${lastRow}`).format.numberFormat='0';
sheet.getRange(`J2:J${lastRow}`).format.numberFormat='$#,##0.00';
const widths=[16,25,16,13,25,18,18,15,12,15,18];
for(let i=0;i<widths.length;i++)sheet.getRange(`${String.fromCharCode(65+i)}:${String.fromCharCode(65+i)}`).format.columnWidth=widths[i];
const table=sheet.tables.add(`A1:K${lastRow}`,true,'SampleTransactions');
table.style='TableStyleMedium2';
table.showFilterButton=true;
const readme=workbook.worksheets.add('Read Me');
readme.showGridLines=false;
readme.getRange('A1:B8').values=[
 ['CUSTOMER PURCHASE ANALYSIS',''],
 ['Excel sample workbook',''],
 ['What is this?','Generated demo data for testing the Customer Purchase Analysis website. These are not real customer or sales records.'],
 ['Rows',recordCount],
 ['How to import','Open the website → Data Management → Choose a file → select this workbook → Validate and import.'],
 ['Data layout','The Transactions sheet contains one row per order line. Order IDs, customer IDs, and product IDs are linked consistently.'],
 ['Revenue calculation','Line revenue is quantity × unit price. Dates span 2024 through 2026.'],
 ['Expected columns','customer_id, customer_name, city, product_id, product_name, category, order_id, order_date, quantity, unit_price, payment_method']
];
readme.getRange('A1:B8').format.font={name:'Arial',size:10,color:'#3B3024'};
readme.getRange('A1:B1').format={fill:'#402B1C',font:{name:'Arial',size:14,bold:true,color:'#E6C15C'},verticalAlignment:'center'};
readme.getRange('A2:B2').format={font:{name:'Arial',size:12,bold:true,color:'#75532E'}};
readme.getRange('A3:A8').format={font:{name:'Arial',size:10,bold:true,color:'#604326'}};
readme.getRange('B3:B8').format.wrapText=true;
readme.getRange('A1:B8').format.verticalAlignment='center';
readme.getRange('A1:B8').format.rowHeight=24;
readme.getRange('A3:B8').format.rowHeight=42;
readme.getRange('A:A').format.columnWidth=25;
readme.getRange('B:B').format.columnWidth=88;
readme.freezePanes.freezeRows(2);
workbook.recalculate();
await fs.mkdir(outputDir,{recursive:true});
const preview=await workbook.render({sheetName:'Transactions',range:'A1:K14',scale:1,format:'png'});
await fs.writeFile(`${outputDir}/preview.png`,new Uint8Array(await preview.arrayBuffer()));
const output=await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/customer_purchase_analysis_sample.xlsx`);
await fs.copyFile(`${outputDir}/customer_purchase_analysis_sample.xlsx`,'data/sample_dataset.xlsx');
await fs.copyFile(`${outputDir}/customer_purchase_analysis_sample.xlsx`,'frontend/public/sample_dataset.xlsx');
console.log(JSON.stringify({rows:recordCount,output:`${outputDir}/customer_purchase_analysis_sample.xlsx`,preview:`${outputDir}/preview.png`}));
