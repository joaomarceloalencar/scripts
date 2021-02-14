BEGIN {
   print "Armazenando Matriculas em Vetor" 
   i = 0
}
{ 
   Alunos[i] = $1
   i = i + 1
}
END {
   printf "Quinta matrícula %d\n", Alunos[4]
} 
