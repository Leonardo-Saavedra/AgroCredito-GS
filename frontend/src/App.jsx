import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'

const API_URL = 'http://127.0.0.1:8000'

const SUGESTOES = [
  'Quais linhas de crédito servem para comprar uma máquina pequena e quanto ficaria a parcela em 36 meses?',
  'O que é o Pronaf e quem pode acessar?',
  'Quais documentos preciso levar ao banco para pedir crédito?',
]

function Folha({ tamanho, cor }) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 64 64" aria-hidden="true">
      <path d="M32 50V30" stroke={cor} strokeWidth="4" strokeLinecap="round" fill="none" />
      <path d="M32 30C32 20 24 14 14 14c0 10 6 16 18 16z" fill={cor} />
      <path d="M32 36c0-8 6-13 14-13 0 8-5 13-14 13z" fill={cor} fillOpacity="0.6" />
    </svg>
  )
}

function App() {
  const [nome, setNome] = useState('Maria')
  const [cafAtivo, setCafAtivo] = useState(true)
  const [categoria, setCategoria] = useState('agricultor_familiar')
  const [finalidade, setFinalidade] = useState('')
  const [valor, setValor] = useState('')

  const valorNumero = Number(valor)
  const perfil = {
    nome: nome.trim(),
    caf_ativo: cafAtivo,
    categoria,
    finalidade: finalidade || null,
    valor_desejado: valorNumero > 0 ? valorNumero : null,
  }
  const nomeValido = perfil.nome.length > 0

  const [pergunta, setPergunta] = useState('')
  const [mensagens, setMensagens] = useState([])
  const [conversaId, setConversaId] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const fimRef = useRef(null)

  useEffect(() => {
    fimRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensagens, carregando])

  async function enviar(textoPronto) {
    const texto = (textoPronto ?? pergunta).trim()
    if (!texto || carregando || !nomeValido) return

    setMensagens((atual) => [...atual, { autor: 'produtor', texto }])
    setPergunta('')
    setCarregando(true)

    try {
      const resposta = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta: texto, perfil, conversaId }),
      })
      if (!resposta.ok) throw new Error('falha')
      const dados = await resposta.json()
      setConversaId(dados.conversaId)
      setMensagens((atual) => [
        ...atual,
        {
          autor: 'assistente',
          texto: dados.resposta,
          fontes: dados.fontes,
          ferramentas: dados.ferramentasUsadas,
        },
      ])
    } catch {
      setMensagens((atual) => [
        ...atual,
        { autor: 'assistente', texto: 'Não foi possível obter a resposta. Tente novamente.', erro: true },
      ])
    } finally {
      setCarregando(false)
    }
  }

  function novaConversa() {
    setMensagens([])
    setConversaId(null)
    setPergunta('')
  }

  return (
    <div className="app">
      <header className="topo">
        <Folha tamanho={40} cor="#ffffff" />
        <div>
          <h1>AgroCrédito</h1>
          <p>Assistente de crédito rural para pequenos produtores</p>
        </div>
      </header>

      <div className="conteudo">
        <aside className="perfil">
          <h2>Perfil do produtor</h2>

          <label>
            Nome
            <input value={nome} maxLength={80} onChange={(e) => setNome(e.target.value)} />
          </label>

          <label className="check">
            <input
              type="checkbox"
              checked={cafAtivo}
              onChange={(e) => setCafAtivo(e.target.checked)}
            />
            CAF ativo
          </label>

          <label>
            Categoria
            <select value={categoria} onChange={(e) => setCategoria(e.target.value)}>
              <option value="agricultor_familiar">Agricultor familiar</option>
              <option value="reforma_agraria">Reforma agrária</option>
              <option value="indigena">Indígena</option>
              <option value="quilombola">Quilombola</option>
            </select>
          </label>

          <label>
            Finalidade
            <select value={finalidade} onChange={(e) => setFinalidade(e.target.value)}>
              <option value="">Não informar</option>
              <option value="investimento">Investimento</option>
              <option value="maquinas">Máquinas</option>
              <option value="habitacao">Habitação</option>
            </select>
          </label>

          <label>
            Valor desejado (R$)
            <input
              type="number"
              min="1"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
            />
          </label>

          <button className="secundario" onClick={novaConversa}>
            Nova conversa
          </button>
        </aside>

        <main className="chat">
          <div className="mensagens" aria-live="polite">
            {mensagens.length === 0 && (
              <div className="vazio">
                <Folha tamanho={56} cor="#2f6b2f" />
                <h2>Como posso ajudar?</h2>
                <p>Pergunte sobre crédito rural ou escolha uma sugestão:</p>
                <div className="sugestoes">
                  {SUGESTOES.map((s) => (
                    <button key={s} className="sugestao" onClick={() => enviar(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {mensagens.map((m, i) => (
              <div key={i} className={`mensagem ${m.autor}${m.erro ? ' erro' : ''}`}>
                <span className="autor">{m.autor === 'produtor' ? 'Você' : 'Assistente'}</span>
                <div className="texto">
                  <ReactMarkdown>{m.texto}</ReactMarkdown>
                </div>
                {m.fontes && m.fontes.length > 0 && (
                  <div className="etiquetas">
                    <span className="rotulo">Fontes</span>
                    {m.fontes.map((f) => (
                      <span key={f.fonte} className="etiqueta">
                        {f.titulo}
                      </span>
                    ))}
                  </div>
                )}
                {m.ferramentas && m.ferramentas.length > 0 && (
                  <div className="etiquetas">
                    <span className="rotulo">Ferramentas</span>
                    {m.ferramentas.map((f) => (
                      <span key={f} className="etiqueta ferramenta">
                        {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {carregando && (
              <div className="carregando" role="status" aria-label="Consultando">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}

            <div ref={fimRef} />
          </div>

          {!nomeValido && (
            <p className="aviso">Informe o nome do produtor no perfil para enviar perguntas.</p>
          )}

          <div className="entrada">
            <input
              aria-label="Digite sua pergunta"
              value={pergunta}
              onChange={(e) => setPergunta(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && enviar()}
              placeholder="Digite sua pergunta"
              maxLength={1000}
            />
            <button onClick={() => enviar()} disabled={carregando || !nomeValido}>
              Enviar
            </button>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App