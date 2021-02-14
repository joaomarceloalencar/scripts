/* Exemplo do IF */
BEGIN { 
   printf "Relatório da Disciplina.\n"
}
{
   nota1 = $NF
   nota2 = $(NF - 1)
   nota3 = $(NF - 2)
   if ((nota1 + nota2 + nota3) / 3 >= 7) {
      aprovados = aprovados + 1
   }
   else {
      reprovados = reprovados + 1
   }
}
END {
   printf "Número de Alunos Reprovados: %d.\n", reprovados
   printf "Número de Alunos Aprovados: %d.\n", aprovados

}
