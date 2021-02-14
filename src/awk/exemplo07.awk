/* Exemplo dicionário */
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
   for (a in media) {
      printf "Aluno: %s, média: %.2f \n", a, media[a]
   }
}
