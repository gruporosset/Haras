// import { Loading } from 'quasar';
// import api from './axios';

// export default () => {  // Remova o parâmetro não utilizado { app }
//   // Interceptor de requisição
//   api.interceptors.request.use((config) => {
//     Loading.show({
//       message: 'Carregando...',
//       boxClass: 'bg-grey-2 text-grey-9',
//       spinnerColor: 'primary'
//     });
//     return config;
//   });

//   // Interceptor de resposta
//   api.interceptors.response.use(
//     (response) => {
//       Loading.hide();
//       return response;
//     },
//     (error) => {
//       Loading.hide();
      
//       // Você pode adicionar tratamento global de erros aqui
//     //   const message = error.response?.data?.message || 
//     //                  error.message || 
//     //                  'Erro na requisição';
      
//       // Se quiser usar notificações globais, você precisaria injetar $q aqui
//       // Mas como estamos em um boot file, seria melhor fazer isso no componente
      
//       return Promise.reject(error);
//     }
//   );
// };