BEGIN { 
   print "Relatório de Valores.";
   valor = 0;
}

$1 !~ /^\*/ { 
   printf "Processando produto %s\n", $1
   valor = valor + $2;
}

END { 
   printf "Valor final: %.2f\n", valor ;
} 
