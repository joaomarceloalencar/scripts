/* Exemplo de Função e Ordenação na própria linguagem. */
function tam(a) {
   k = 0
   for (i in a) k++
   return k
}

BEGIN { 
   printf "Relatório da Disciplina.\n" >> "relatorio.txt"
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
  
   print "" >> "relatorio.txt"
   print "Original:" >> "relatorio.txt"
   for (i = 1; i <= t; i++) {
      printf "%.2f %-30s\n", media[aluno[i]], aluno[i] >> "relatorio.txt"
   }

   for (i = 1; i <= t; i++) {
      menorMedia = media[aluno[i]] 
      for (j = i + 1; j <= t; j++) {
         if (media[aluno[j]] < menorMedia) {
            menorMedia = media[aluno[j]]
            temp = aluno[i]
            aluno[i] = aluno[j]
            aluno[j] = temp
         }
      }
   }

   print "" >> "relatorio.txt"
   print "Ordenado:" >> "relatorio.txt"
   for (i = 1; i <= t; i++) {
      printf "%.2f %-30s\n", media[aluno[i]], aluno[i] >> "relatorio.txt"
   }
}
