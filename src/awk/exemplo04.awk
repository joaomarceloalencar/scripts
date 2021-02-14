
 tolower((substr($2, 0, 1))) != tolower((substr($NF, 0, 1)))   {  
   primeiraLetraNome = tolower((substr($2, 0, 1)))
   primeiraLetraEmail = tolower((substr($NF, 0, 1)))
   print;
   printf "%c %c\n", primeiraLetraNome, primeiraLetraEmail
} 
