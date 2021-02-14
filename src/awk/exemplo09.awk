/* Exemplo de Ordenação usando "sort". */
function tam(a) {
   k = 0
   for (i in a) k++
   return k
}

BEGIN { 
   printf "Relatório da Disciplina.\n"
   i = 1
}
{
   nome = ""
   j = 1
   while (j < (NF - 2)) {
      nome = nome $j " "
      j = j + 1
   }
   aluno[i] = nome
   
   nota = ($NF + $(NF - 1) + $(NF - 2)) / 3
   media[aluno[i]] = nota

   i = i + 1
}
END {
   t = tam(aluno)
  
   print ""
   print "Original:"
   for (i in aluno) {
      printf "%.2f %-30s\n", media[aluno[i]], aluno[i]  
   }

   print ""
   print "Ordenado:"
   for (i in aluno) {
      printf "%.2f %-30s\n", media[aluno[i]], aluno[i] | "sort -n" 
   } 
}
