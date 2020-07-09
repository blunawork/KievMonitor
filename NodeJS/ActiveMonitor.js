'use strict';

/* 

	Description: 

		Output of system stats JSON.

	Output: 

{ status: 200,
  success: '{"web-x1":{"disk":"90.00","cpu":"21.08","swap":"62.66","mem":"97.44"},"web-x2":{"disk":"78.00","cpu":"6.25","swap":"13.00","mem":"35.82"},"web-x3":{"disk":"45.00","cpu":"4.38","swap":"0.00","mem":"77.67"},"web-x4":{"disk":"81.00","cpu":"34.88","swap":"48.79","mem":"93.28"},"web-x5":{"disk":"52.00","cpu":"3.88","swap":"82.57","mem":"94.56"},"web-x6":{"disk":"44.00","cpu":"22.12","swap":"0.00","mem":"87.85"},"web-x7":{"disk":"48.00","cpu":"15.38","swap":"32.07","mem":"92.81"},"web-x8":{"disk":"79.00","cpu":"14.50","swap":"4.72","mem":"95.79"},"web-x9":{"disk":"73.00","cpu":"9.12","swap":"13.64","mem":"94.34"}}' }

*/

exports.ActiveMonitor = class { 

	// Lookup single or multiple.
	async init( args ) {

		args = args || [];

		let req  = args['req'];
		let res  = args['res'];
		let body = args['body'];

		const Output = global.objects.Output.obj;

		res.setHeader( 'Content-Type', 'application/json' );

		// Response.
		let host_stats = await this.fetch_stats();
		let reply      = await Output.init( { input: host_stats, output_type: 'json' } );

		let result     = {};
		result.status  = 200;
		result.success = reply;

		return result;
	}

	// Combine all records into a single result.
	async fetch_stats( args ) { 

		args = args || [];

		const DBISimple = global.objects.DBISimple.obj;

		let sql   = "select host,json from default-config.SystemStats where type = 'm'";
		let fetch = await DBISimple.fetch( { sql: sql } );  

		let result = {};

		if ( fetch.success && fetch.success.length ) {

			fetch = fetch.success;
	
			for ( let l in fetch ) { 
				let v    = fetch[ l ];
				let host = v.host;

				result[ host ] = JSON.parse( v.json );
			}
		}

		return result;
	}
}
