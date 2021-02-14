/* Exemplo do WHILE */
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
   i = i + 1
}
END {
   for (i = 1; i <= NR; i++) {
      printf "Aluno [%d]: %s\n", i, aluno[i]
   }
}
